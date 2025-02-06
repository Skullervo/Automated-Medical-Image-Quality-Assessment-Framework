from fastapi import FastAPI, HTTPException, Response
import requests
import os

app = FastAPI()

# Orthancin URL (voidaan muuttaa ympäristömuuttujilla)
ORTHANC_URL = os.getenv("ORTHANC_URL", "http://localhost:8042")

@app.get("/")
async def home():
    """Tervetulosivu testaukseen"""
    return {"message": "Fetch Service is running!"}

@app.get("/fetch/{instance_id}")
async def fetch_dicom_data(instance_id: str):
    """Hakee DICOM-tiedoston Orthanc-palvelimelta ja palauttaa sen binääritiedostona"""
    try:
        # Haetaan DICOM-tiedosto Orthancista
        r = requests.get(f"{ORTHANC_URL}/instances/{instance_id}/file")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Failed to fetch DICOM file for instance {instance_id}")
        
        # Palautetaan DICOM-tiedosto binäärimuodossa
        return Response(content=r.content, media_type="application/dicom")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



