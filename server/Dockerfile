# Käytä Python 3.12.5 -kuvaa pohjana
FROM python:3.12.5-slim

# Päivitä ja asenna tarvittavat järjestelmäriippuvuudet
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Työskentelyhakemisto kontille
WORKDIR /app

# Kopioi kaikki tarvittavat tiedostot kontin sisälle
COPY mainAnalysis.py /app/
COPY ultraSoundAnalysis.py /app/
COPY US_IQ_analysis3.py /app/
COPY Requirements.txt /app/
COPY pathSetup.py /app/
COPY LUT_table_codes.py /app/
COPY LUT_taulukko_lisaa.py /app/

# Asenna Python-riippuvuudet
RUN pip install --no-cache-dir -r Requirements.txt

# Aseta oletuskäsky, kun kontti käynnistetään
CMD ["python", "mainAnalysis.py"]
