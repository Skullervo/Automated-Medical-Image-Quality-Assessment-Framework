import requests
import numpy as np
import pydicom
from PIL import Image
from io import BytesIO

# Orthanc-palvelimen URL
orthanc_url = 'http://localhost:8042'
orthanc_username = 'admin'  # Korvaa oikealla käyttäjätunnuksella
orthanc_password = 'alice'  # Korvaa oikealla salasanalla

# Korvaa tämä oikealla instance-arvolla
instance_id = '1dca59da-e58accee-a6f4e288-996e9584-5d460211'

def load_image_from_orthanc(instance_id):
    try:
        # Lataa DICOM-kuva paikalliselta Orthanc-palvelimelta
        r = requests.get(
            f'{orthanc_url}/instances/{instance_id}/file',
            auth=(orthanc_username, orthanc_password)
        )
        r.raise_for_status()
        dicom_file = BytesIO(r.content)
        
        #print(dicom_file)

        # Lue DICOM-tiedosto
        # dicom_data = pydicom.dcmread(dicom_file)
        
        # Lue DICOM-tiedosto käyttäen force=True, jos otsikko puuttuu
        dicom_data = pydicom.dcmread(dicom_file, force=True)
        
        print(dicom_data)
        
        # ds = pydicom.filereader.dcmread(filepath)

        # Muunna DICOM-kuva numpy-taulukoksi
        image_array = dicom_data.pixel_array

        # Muunna numpy-taulukko PIL-kuvaksi
        img = Image.fromarray(image_array)

        # Tallenna kuva PNG-muodossa
        img.save('downloaded_image.png')
        print("Kuva ladattu ja tallennettu onnistuneesti.")
    except Exception as e:
        print(f"Virhe kuvan lataamisessa: {e}")

# Kutsu funktiota
load_image_from_orthanc(instance_id)