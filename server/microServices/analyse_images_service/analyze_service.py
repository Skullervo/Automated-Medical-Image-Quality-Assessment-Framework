import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException
import requests
import json
import numpy as np
import io
import psycopg2
import pydicom
from pydicom.errors import InvalidDicomError
from US_IQ_analysis3 import imageQualityUS

app = FastAPI()

FETCH_SERVICE_URL = os.getenv("FETCH_SERVICE_URL", "http://localhost:8001/fetch")
ORTHANC_URL = os.getenv("ORTHANC_URL", "http://localhost:8042")

DB_CONFIG = {
    "dbname": os.getenv("DATABASE_NAME", "QA-results"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "pohde24"),
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": os.getenv("DATABASE_PORT", "5432"),
}

def connect_db():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ultrasound (
            id SERIAL PRIMARY KEY,
            institutionname TEXT,
            institutionaldepartmentname TEXT,
            manufacturer TEXT,
            modality TEXT,
            stationname TEXT,
            seriesdate TEXT,
            instance TEXT,
            serie TEXT,
            S_depth FLOAT,
            U_cov FLOAT,
            U_skew FLOAT,
            U_low FLOAT[]
        )
    """)
    conn.commit()
    cur.close()
    return conn

@app.get("/")
async def home():
    return {"message": "Analysis Service is running!"}

@app.post("/analyze/{series_id}")
async def analyze_dicom_data(series_id: str):
    """Hakee ja analysoi DICOM-kuvat sekä tallentaa tulokset tietokantaan"""
    try:
        conn = connect_db()
        cur = conn.cursor()

        # Tarkistetaan, onko sarja jo analysoitu
        cur.execute("SELECT COUNT(*) FROM ultrasound WHERE serie = %s", (series_id,))
        result = cur.fetchone()
        if result[0] > 0:
            cur.close()
            conn.close()
            return {"message": "Sarja on jo analysoitu"}

        # Haetaan sarjan tiedot Orthancista
        r = requests.get(f"{ORTHANC_URL}/series/{series_id}")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Series {series_id} not found in Orthanc")

        dicomData = r.json()
        instance_ids = dicomData["Instances"]
        instance_count = len(instance_ids)
        print(f"🔍 Instanssien lukumäärä sarjassa: {instance_count}")

        for instance_id in instance_ids:
            print(instance_id)
            response = requests.get(f"{FETCH_SERVICE_URL}/{instance_id}")
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch DICOM data for instance {instance_id}")

            dicom_bytes = io.BytesIO(response.content)
            try:
                dicom_dataset = pydicom.dcmread(dicom_bytes, force=True)
            except InvalidDicomError as e:
                print(f"Invalid DICOM file: {e}")
                continue

            metadata = {
                "InstitutionName": dicom_dataset.get("InstitutionName", "Unknown"),
                "InstitutionalDepartmentName": dicom_dataset.get("InstitutionalDepartmentName", "Unknown"),
                "Manufacturer": dicom_dataset.get("Manufacturer", "Unknown"),
                "Modality": dicom_dataset.get("Modality", "Unknown"),
                "StationName": dicom_dataset.get("StationName", "Unknown"),
                "SeriesDate": dicom_dataset.get("SeriesDate", "Unknown")
            }

            if metadata["Modality"] != "US":
                continue  # Skip non-ultrasound images

            image_array = dicom_dataset.pixel_array

            analysis = imageQualityUS(dicom_dataset, dicom_bytes, image_array, "probe-LUT.xls")
            result = analysis.MAIN_US_analysis()

            json_result = {}
            for key, value in result.items():
                if isinstance(value, np.ndarray):
                    json_result[key] = value.tolist()
                elif isinstance(value, np.float64):
                    json_result[key] = float(value)
                elif isinstance(value, pydicom.dataset.FileDataset):
                    json_result[key] = str(value)
                else:
                    json_result[key] = value

            cur.execute("""
                INSERT INTO ultrasound (
                institutionname, institutionaldepartmentname, manufacturer, modality, 
                stationname, seriesdate, instance, serie, S_depth, U_cov, U_skew, U_low
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                metadata["InstitutionName"],
                metadata["InstitutionalDepartmentName"],
                metadata["Manufacturer"],
                metadata["Modality"],
                metadata["StationName"],
                metadata["SeriesDate"],
                instance_id,
                series_id,
                float(json_result['S_depth']),
                float(json_result['U_cov']),
                float(json_result['U_skew']),
                [float(val) for val in json_result['U_low']]
            ))

        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "Analyysi suoritettu ja tallennettu tietokantaan!",
            "series_id": series_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




