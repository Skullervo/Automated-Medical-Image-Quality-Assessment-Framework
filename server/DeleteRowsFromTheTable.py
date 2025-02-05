# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 12:12:24 2024

@author: sylisiur
"""

import psycopg2

# Yhdistä tietokantaan
conn = psycopg2.connect(
    dbname="Orthanc",
    user="postgres",
    password="YliSkullervo_87",
    host="localhost",
    port="5432"
    )

# Luo kurssori
cur = conn.cursor()

# Suorita SQL-kysely analysoitavan taulun rivien poistamiseksi
cur.execute("DELETE FROM series")

# Vahvista muutokset
conn.commit()

# Sulje kurssori ja yhteys
cur.close()
conn.close()
