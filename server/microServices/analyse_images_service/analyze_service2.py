import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, HTTPException
import requests
import json
import numpy as np
import io
import pydicom
from pydicom.errors import InvalidDicomError
from US_IQ_analysis3 import imageQualityUS

app = FastAPI()

FETCH_SERVICE_URL = os.getenv("FETCH_SERVICE_URL", "http://localhost:8001/fetch")
ORTHANC_URL = os.getenv("ORTHANC_URL", "http://localhost:8042")

# Määritä oikea polku probe-LUT.xls-tiedostolle
PROBE_LUT_PATH = os.path.join(os.path.dirname(__file__), "probe-LUT.xls")

@app.get("/")
async def home():
    return {"message": "Analysis Service is running!"}

@app.post("/analyze/{series_id}")
async def analyze_dicom_data(series_id: str):
    """Hakee ja analysoi DICOM-kuvat ja palauttaa analysoidut tulokset"""
    try:
        # Haetaan sarjan tiedot Orthancista
        r = requests.get(f"{ORTHANC_URL}/series/{series_id}")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Series {series_id} not found in Orthanc")

        dicomData = r.json()
        instance_ids = dicomData["Instances"]
        instance_count = len(instance_ids)
        print(f"🔍 Instanssien lukumäärä sarjassa: {instance_count}")

        all_results = []

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

            analysis = imageQualityUS(dicom_dataset, dicom_bytes, image_array, PROBE_LUT_PATH)
            result = analysis.MAIN_US_analysis()

            json_result = {}
            for key, value in result.items():
                if isinstance(value, np.ndarray):
                    json_result[key] = value.tolist()
                elif isinstance(value, (np.float32, np.float64)):
                    json_result[key] = float(value)
                elif isinstance(value, pydicom.dataset.FileDataset):
                    json_result[key] = str(value)
                else:
                    json_result[key] = value

            all_results.append({
                "metadata": metadata,
                "results": json_result,
                "instance_id": instance_id,
                "series_id": series_id
            })

        return {
            "message": "Analyysi suoritettu!",
            "series_id": series_id,
            "results": all_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))