import psycopg2
import requests
import json
import pydicom
from US_IQ_analysis3 import imageQualityUS
import numpy as np
import io


def connectPostgre(dataBase):
    
    # Make connection to the db
    
    conn = psycopg2.connect(
                   dbname=dataBase,
                   user="postgres",
                   password="pohde24",
                   host="localhost",
                   port="5432"
                   )
    
    return conn


def createTablePostgre(cur):
    
    # Execute the SQL command to create a new table
    
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
    
    """
    Updates the 'series' database table by adding new rows that have not yet been added.

    Args:
    cur (cursor): A database cursor object on which to execute SQL queries.
    rows (list): List of rows containing the data to be inserted.
    series_waiting_analysis (list): List to add rows waiting for analysis.

    Returns:
    None
    """
            
    for row in rows:
        
        # Check if the row is already in the 'series' array
        
        cur.execute("SELECT COUNT(*) FROM series WHERE \"internalid\" = %s AND resourcetype = %s::VARCHAR AND publicid = %s::VARCHAR", (row[0], row[1], row[2]))
        count = cur.fetchone()[0]

        # Add row 'series' to array if not found
        
        if count == 0:
            
            cur.execute("INSERT INTO series (\"internalid\", resourcetype, publicid) VALUES (%s, %s, %s)", (row[0], row[1], row[2]))
            print("Data successfully added to analyzedstudies table.")
            
            # Add row to studiesWaitingAnalysis list if not already added
            
            seriesWaitingAnalysis.append(row)
            
        else:
            
            print("No new lines")
            
    return seriesWaitingAnalysis
            


def fetchAndProcessDicomData(seriesWaitingAnalysis):
    
    """
    Retrieves DICOM series data from the Orthanc server and processes the received images.

    Args:
    orthanc_url (str): Orthanc server URL.
    series_waiting_analysis (list): List of series waiting to be processed.

    Returns:
    None
    """
    
    # Initializing the Orthanc REST API address and port
    
    orthancUrl = "http://localhost:8042"
    
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
        print(image.shape)  # image shape
        
        imageReshaped = np.squeeze(image)
        print(imageReshaped.shape)  # Prints the dimensions of the reshaped image
        
    return dicomData, instance, jsonInstances, modality, image, imageReshaped




def analyseDicomImages(orthanc_url, seriesWaitingAnalysis, table, connOrthanc, connQAresults, cur):
    
    try:
        
        for ii in range(len(seriesWaitingAnalysis)):
            
            print('serie')
            print(ii)
        
            serieWaitingAnalysis = seriesWaitingAnalysis[ii][2]
        
            r = requests.get(f'{orthanc_url}/series/{serieWaitingAnalysis}')
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

            # Check that the content is not empty
            
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
        
            # Check the modality of the images and perform LV analysis accordingly
            
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
                            )
                        )
                
                
                    # Confirm changes
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
                                    )
                                )
                
                    # Confirm changes
                    connQAresults.commit()
                    
            else:
                
                print("no US image")
   
        # Close connection
        cur.close()
        connQAresults.close()         
        connOrthanc.close()
    
    except IndexError as e:
        
        print("The index of the list exceeds list size:", e)
        print(range(image_reshaped.shape))
        print(range(image_reshaped.shape[0]))

