from fastapi import FastAPI, HTTPException
import psycopg2
import os

app = FastAPI()

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
    return {"message": "Save Results Service is running!"}

@app.post("/save_results")
async def save_results(data: dict):
    """Tallentaa analysoidut tulokset tietokantaan"""
    try:
        conn = connect_db()
        cur = conn.cursor()

        for result in data["results"]:
            metadata = result["metadata"]
            json_result = result["results"]
            instance_id = result["instance_id"]
            series_id = result["series_id"]

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

        return {"message": "Tulokset tallennettu tietokantaan!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
