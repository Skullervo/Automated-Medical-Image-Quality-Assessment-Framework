import subprocess
import time
import requests
import json
import os

# 🛠 Määritä Pythonin polku virtuaaliympäristöstä
PYTHON_PATH = "C:\\Users\\sylisiur\\Projects\\LV-automaatti\\server\\venvUS\\Scripts\\python.exe"

def start_service(command):
    """ Käynnistää mikropalvelun taustaprosessina ja palauttaa prosessin. """
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def check_service_ready(url, retries=10, delay=2):
    """ Tarkistaa, että palvelu on käynnissä ennen kuin jatketaan. """
    for _ in range(retries):
        try:
            response = requests.get(url)
            if response.status_code in {200, 404, 405}:
                print(f"✅ {url} palvelu on käynnissä!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(delay)
    print(f"❌ {url} ei vastaa. Tarkista palvelun tila.")
    return False

def main():
    services = [
        (f"{PYTHON_PATH} -m uvicorn microServices.fetch_images_service.main:app --host 0.0.0.0 --port 8001", "http://localhost:8001/docs"),
        (f"{PYTHON_PATH} -m uvicorn microServices.analyse_images_service.main:app --host 0.0.0.0 --port 8002", "http://localhost:8002/docs"),
        (f"{PYTHON_PATH} -m uvicorn microServices.store_results_service.main:app --host 0.0.0.0 --port 8003", "http://localhost:8003/docs")
    ]

    processes = []
    for service_command, service_url in services:
        print(f"🔄 Käynnistetään: {service_command}")
        process = start_service(service_command)
        processes.append((process, service_url))
        time.sleep(1)  # Odota hetki, jotta palvelut eivät käynnisty yhtä aikaa

    # ✅ Varmista, että kaikki palvelut ovat käynnissä
    for process, service_url in processes:
        if not check_service_ready(service_url):
            print(f"❌ Palvelu {service_url} ei vastaa! Sammutetaan kaikki prosessit.")
            for proc, _ in processes:
                proc.terminate()
            return

    print("✅ Kaikki palvelut käynnissä, aloitetaan analyysi!")

    # 📌 Suorita analyysi
    orthanc_url = 'http://localhost:8042'
    seriesWaitingAnalysis = [["123", "US", "SERIES_001"]]
    table = 'probe-LUT.xls'

    analyse_url = 'http://localhost:8002/analyse/'
    analyse_data = {
        'seriesWaitingAnalysis': seriesWaitingAnalysis,
        'orthanc_url': orthanc_url,
        'table': table
    }

    try:
        print(f"📡 Lähetetään analyysipyyntö: {analyse_url}")
        analyse_response = requests.post(analyse_url, json=analyse_data)

        if analyse_response.status_code != 200:
            print(f"❌ Analyysipyyntö epäonnistui: {analyse_response.text}")
            return
        
        analysis_results = analyse_response.json()
        print(f"📊 Analyysitulokset: {json.dumps(analysis_results, indent=2)}")

        # 📌 Tallenna analyysitulokset tietokantaan
        store_url = 'http://localhost:8003/store/'
        store_response = requests.post(store_url, json={'data': analysis_results})

        if store_response.status_code != 200:
            print(f"❌ Tallennus epäonnistui: {store_response.text}")
            return
        
        print(f"💾 Tietojen tallennus onnistui: {store_response.json()}")

    except KeyboardInterrupt:
        print("\n🛑 Keskeytys havaittu, suljetaan palvelut...")
        for process, _ in processes:
            process.terminate()

if __name__ == '__main__':
    main()
