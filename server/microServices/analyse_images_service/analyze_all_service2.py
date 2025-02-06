from fastapi import FastAPI, HTTPException
import requests
import os

app = FastAPI()

ANALYZE_SERVICE_URL = os.getenv("ANALYZE_SERVICE_URL", "http://localhost:8002/analyze")
SAVE_RESULTS_SERVICE_URL = os.getenv("SAVE_RESULTS_SERVICE_URL", "http://localhost:8004/save_results")
ORTHANC_URL = os.getenv("ORTHANC_URL", "http://localhost:8042")

@app.get("/")
async def home():
    return {"message": "Analyze All Service is running!"}

@app.post("/analyze_all")
async def analyze_all_series():
    """Hakee ja analysoi kaikki DICOM-sarjat Orthancista, jos niitä ei ole vielä analysoitu"""
    try:
        # Haetaan kaikki sarjat Orthancista
        r = requests.get(f"{ORTHANC_URL}/series")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail="Failed to fetch series from Orthanc")

        series_list = r.json()
        for series_id in series_list:
            # Kutsutaan analyze_service-palvelua analysoimaan jokainen sarja
            response = requests.post(f"{ANALYZE_SERVICE_URL}/{series_id}")
            if response.status_code != 200:
                print(f"Failed to analyze series {series_id}: {response.content}")
                continue

            analysis_results = response.json()
            # Kutsutaan save_results_service-palvelua tallentamaan analysoidut tulokset
            save_response = requests.post(SAVE_RESULTS_SERVICE_URL, json=analysis_results)
            if save_response.status_code != 200:
                print(f"Failed to save results for series {series_id}: {save_response.content}")

        return {"message": "Kaikki sarjat on analysoitu!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))