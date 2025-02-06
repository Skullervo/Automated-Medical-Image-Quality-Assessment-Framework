import pydicom

# Lue ladattu DICOM-tiedosto
dicom_dataset = pydicom.dcmread("testikuva.dcm")

# ✅ Tarkistetaan metatiedot
print("Modality:", dicom_dataset.Modality)
print("Manufacturer:", dicom_dataset.Manufacturer)
print("SeriesDate:", dicom_dataset.SeriesDate)

# ✅ Tarkistetaan kuvadata
if hasattr(dicom_dataset, "pixel_array"):
    print("Kuvadata löytyi! Kuvan muoto:", dicom_dataset.pixel_array.shape)
else:
    print("⚠️ Kuvadata puuttuu!")