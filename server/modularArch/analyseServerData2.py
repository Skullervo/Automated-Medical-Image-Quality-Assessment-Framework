from pathSetup import setupIqToolPath
from US_IQ_analysis3 import imageQualityUS
from serverConnections import connectPostgre, createTablePostgre, updateSeriesDatabase, analyseDicomImages
import os

def clear_table(cursor, table_name):
    cursor.execute(f"DELETE FROM {table_name}")

import os

def main():
    setupIqToolPath()

    # Create database connection and table for QA-results
    dataBase = "QA-results"
    connQAresults = connectPostgre(dataBase)
    curQAresults = connQAresults.cursor()
    createTablePostgre(curQAresults)
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
    #clear_table(curOrthanc1, "patients")
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

if __name__ == '__main__':
    main()


