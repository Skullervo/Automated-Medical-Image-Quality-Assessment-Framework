import os
from pathSetup import setupIqToolPath
import psycopg2
import requests
import json
import pydicom
from US_IQ_analysis3 import imageQualityUS
import numpy as np
import io

def connectPostgre(dataBase):
    conn = psycopg2.connect(
        dbname=dataBase,
        user="postgres",
        password="pohde24",
        host="localhost",
        port="5432"
    )
    # conn = psycopg2.connect(
    #     dbname=os.getenv("DATABASE_NAME", "QA-results"),
    #     user=os.getenv("DATABASE_USER", "postgres"),
    #     password=os.getenv("DATABASE_PASSWORD", "pohde24"),
    #     host=os.getenv("DATABASE_HOST", "localhost"),
    #     port=os.getenv("DATABASE_PORT", "5432")
    # )
    return conn

def createTableUltraSound(cur):
    cur.execute("""
        CREATE TABLE ultrasound (
        id SERIAL PRIMARY KEY,
        institutionname TEXT,
        institutionaldepartmentname TEXT,
        manufacturer TEXT,
        modality TEXT,
        stationname TEXT,
        seriesdate TEXT,
        instance TEXT,
        serie TEXT,
        s_depth NUMERIC,
        u_cov NUMERIC,
        u_skew NUMERIC,
        u_low FLOAT8[]
        )
    """)

def updateSeriesDatabase(cur, rows, seriesWaitingAnalysis):
    for row in rows:
        cur.execute("SELECT COUNT(*) FROM series WHERE \"internalid\" = %s AND resourcetype = %s::VARCHAR AND publicid = %s::VARCHAR", (row[0], row[1], row[2]))
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute("INSERT INTO series (\"internalid\", resourcetype, publicid) VALUES (%s, %s, %s)", (row[0], row[1], row[2]))
            print("Data successfully added to analyzedstudies table.")
            seriesWaitingAnalysis.append(row)
        else:
            print("No new lines")
    return seriesWaitingAnalysis

def fetchAndProcessDicomData(seriesWaitingAnalysis):
    orthancUrl = os.getenv("ORTHANC_URL", "http://localhost:8042")
    for ii, series in enumerate(seriesWaitingAnalysis):
        print('serie')
        print(ii)
        serieID = series[2]
        r = requests.get(f'{orthancUrl}/series/{serieID}')
        dicomData = json.loads(r.content)
        instance = dicomData["Instances"][0]
        r = requests.get(f'{orthancUrl}/instances/{instance}/simplified-tags')
        jsonInstances = json.loads(r.content)
        modality = jsonInstances.get("Modality")
        print()
        r = requests.get(f'{orthancUrl}/series/{serieID}/numpy')
        r.raise_for_status()
        image = np.load(io.BytesIO(r.content))
        print(image.shape)
        imageReshaped = np.squeeze(image)
        print(imageReshaped.shape)
    return dicomData, instance, jsonInstances, modality, image, imageReshaped

def analyseDicomImages(orthanc_url, seriesWaitingAnalysis, table, connOrthanc, connQAresults, cur):
    try:
        for ii in range(len(seriesWaitingAnalysis)):
            # AUTH = ("admin", "alice")
            print('serie')
            print(ii)
            serieWaitingAnalysis = seriesWaitingAnalysis[ii][2]
            # r = requests.get(f'{orthanc_url}/series/{serieWaitingAnalysis}', auth=AUTH)
            r = requests.get(f'{orthanc_url}/series/{serieWaitingAnalysis}')
            # print(f"Requesting URL: {orthanc_url}/series/{serieID}")
            print(f"Response status: {r.status_code}")
            print(f"Response content: {r.text}")  # TÄRKEÄ DEBUG-TULOSTE
            dicomData = json.loads(r.content)
            instance = dicomData["Instances"][0]
            r = requests.get(f'{orthanc_url}/instances/{instance}/simplified-tags')
            jsonInstances = json.loads(r.content)
            modality = jsonInstances["Modality"]
            r = requests.get(f'{orthanc_url}/series/{serieWaitingAnalysis}/numpy')
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"HTTP error occurred: {e}")
                print(f"Response content: {r.content}")
                continue
            if len(r.content) == 0:
                print(f"Skipping empty image for series {serieWaitingAnalysis}")
                continue
            try:
                image = np.load(io.BytesIO(r.content))
                print(image.shape)
            except Exception as e:
                print(f"Failed to load image for series {serieWaitingAnalysis}: {e}")
                continue
            image_reshaped = np.squeeze(image)
            print(image_reshaped.shape)
            if modality == 'US':
                if image.shape[0] == 1:
                    print('image')
                    print(ii)
                    instance = dicomData["Instances"][0]
                    url_instance = f'{orthanc_url}/instances/{instance}/file'
                    r = requests.get(url_instance)
                    dicom_bytes = io.BytesIO(r.content)
                    dicom_dataset = pydicom.dcmread(dicom_bytes)
                    manufacturer = jsonInstances["Manufacturer"]
                    stationname = jsonInstances["StationName"]
                    seriesdate = jsonInstances["SeriesDate"]
                    institutionname = jsonInstances["InstitutionName"]
                    institutionaldepartmentname = jsonInstances["InstitutionalDepartmentName"]
                    w = imageQualityUS(dicom_dataset, dicom_bytes, image_reshaped, table)
                    result = w.MAIN_US_analysis()
                    u_low_values = [float(val) for val in result['U_low']]
                    cur.execute("""
                        INSERT INTO ultrasound (institutionname, institutionaldepartmentname, manufacturer, modality, stationname, seriesdate, instance, serie, S_depth, U_cov, U_skew, U_low) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                        institutionname,
                        institutionaldepartmentname,
                        manufacturer,
                        modality,
                        stationname,
                        seriesdate,
                        instance,
                        serieWaitingAnalysis,
                        float(result['S_depth']),
                        float(result['U_cov']),
                        float(result['U_skew']),
                        u_low_values
                    ))
                    connQAresults.commit()
                else:
                    print(modality)
                    for jj in range(image_reshaped.shape[0]):
                        print('image')
                        print(jj)
                        instance = dicomData["Instances"][jj]
                        url_instance = f'{orthanc_url}/instances/{instance}/file'
                        r = requests.get(url_instance)
                        dicom_bytes = io.BytesIO(r.content)
                        dicom_dataset = pydicom.dcmread(dicom_bytes)
                        manufacturer = jsonInstances["Manufacturer"]
                        stationname = jsonInstances["StationName"]
                        seriesdate = jsonInstances["SeriesDate"]
                        institutionname = jsonInstances["InstitutionName"]
                        institutionaldepartmentname = jsonInstances["InstitutionalDepartmentName"]
                        w = imageQualityUS(dicom_dataset, dicom_bytes, image_reshaped[jj,:,:], table)
                        result = w.MAIN_US_analysis()
                        u_low_values = [float(val) for val in result['U_low']]
                        cur.execute("""
                            INSERT INTO ultrasound (institutionname, institutionaldepartmentname, manufacturer, modality, stationname, seriesdate, instance, serie, S_depth, U_cov, U_skew, U_low) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                            institutionname,
                            institutionaldepartmentname,
                            manufacturer,
                            modality,
                            stationname,
                            seriesdate,
                            instance,
                            serieWaitingAnalysis,
                            float(result['S_depth']),
                            float(result['U_cov']),
                            float(result['U_skew']),
                            u_low_values
                        ))
                    connQAresults.commit()
            else:
                print("no US image")
        cur.close()
        connQAresults.close()
        connOrthanc.close()
    except IndexError as e:
        print("The index of the list exceeds list size:", e)
        print(range(image_reshaped.shape))
        print(range(image_reshaped.shape[0]))
        
def clear_table(cursor, table_name):
    cursor.execute(f"DELETE FROM {table_name}")

def runUltraSoundAnalysis():
    setupIqToolPath()

    # Create database connection and table for QA-results
    dataBase = "QA-results"
    connQAresults = connectPostgre(dataBase)
    curQAresults = connQAresults.cursor()
    createTableUltraSound(curQAresults)
    connQAresults.commit()
    curQAresults.close()
    connQAresults.close()

    # Clear the data in the QA-results database table (for test purposes, removed from the final version)
    connQAresults = connectPostgre(dataBase)
    curQAresults = connQAresults.cursor()
    clear_table(curQAresults, "ultrasound")
    connQAresults.commit()
    curQAresults.close()
    connQAresults.close()

    # Clear the data of the Orthanc database tables (for test purposes, removed from the final version)
    dataBase = "Orthanc"
    connOrthanc = connectPostgre(dataBase)
    curOrthanc1 = connOrthanc.cursor()
    curOrthanc2 = connOrthanc.cursor()
    curOrthanc3 = connOrthanc.cursor()
    clear_table(curOrthanc2, "series")
    curOrthanc3.execute("SELECT * FROM orthancseriesids")
    connOrthanc.commit()
    rows3 = curOrthanc3.fetchall()
    curOrthanc1.close()
    curOrthanc2.close()

    # Updating the series database
    seriesWaitingAnalysis = updateSeriesDatabase(curOrthanc3, rows3, [])
    curOrthanc3.close()
    connOrthanc.close()

    # Set the working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Current working directory
    baseDir = os.getcwd()
    print("Current working directory:", baseDir)

    # Path for probe table
    table = os.path.join(script_dir, 'probe-LUT.xls')

    # Orthanc url
    orthanc_url = 'http://localhost:8042'

    # Perform analysis of DICOM images
    connQAresults = connectPostgre("QA-results")
    connOrthanc = connectPostgre("Orthanc")
    curQAresults = connQAresults.cursor()
    analyseDicomImages(orthanc_url, seriesWaitingAnalysis, table, connOrthanc, connQAresults, curQAresults)
    curQAresults.close()
    connQAresults.close()
    connOrthanc.close()


