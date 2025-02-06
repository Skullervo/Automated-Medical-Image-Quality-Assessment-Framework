# Alustukset
from pathSetup import setupIqToolPath
setupIqToolPath()
from US_IQ_analysis3 import imageQualityUS
from serverConnections import connectPostgre, createTablePostgre, updateSeriesDatabase, analyseDicomImages
import os

def main():
    setupIqToolPath()

    # Create database connection and table
    dataBase = "QA-results" #database where analysis results are updated
    conn = connectPostgre(dataBase)
    cur = conn.cursor()
    createTablePostgre(cur)
    conn.commit()
    cur.close()
    conn.close()

    # Clear the data in the QA-results database table
    connQAresults = connectPostgre(dataBase)
    cur1 = connQAresults.cursor()
    cur1.execute("DELETE FROM ultrasound")
    connQAresults.commit()
    cur1.close()

    # Clear the data of the Orthanc database tables
    dataBase = "Orthanc"
    connOrthanc = connectPostgre(dataBase)
    cur1 = connOrthanc.cursor()
    cur2 = connOrthanc.cursor()
    cur3 = connOrthanc.cursor()
    #cur1.execute("DELETE FROM patients")
    cur2.execute("DELETE FROM series")
    #cur3.execute("SELECT * FROM orthancserieids")
    connOrthanc.commit()
    cur1.close()
    cur2.close()

    rows3 = cur3.fetchall()
    # cur3.close()

    # Updating the series database
    seriesWaitingAnalysis = updateSeriesDatabase(cur3, rows3, [])

    # Perform analysis of DICOM images
    # Määritä tiedoston suhteellinen polku
    #relativePath = os.path.join('probe-LUT.xls')

    # Hae nykyinen työskentelyhakemisto
    baseDir = os.getcwd()

    # Muodosta absoluuttinen polku suhteellisen polun perusteella
    table = os.path.join(baseDir, 'probe-LUT.xls')
    
    #table = "C:/Users/sylisiur/Desktop/QAtest/server/probe-LUT.xls"
    orthanc_url = 'http://localhost:8042'
    analyseDicomImages(orthanc_url, seriesWaitingAnalysis, table, connOrthanc, connQAresults, connQAresults.cursor())

if __name__ == '__main__':
    main()
