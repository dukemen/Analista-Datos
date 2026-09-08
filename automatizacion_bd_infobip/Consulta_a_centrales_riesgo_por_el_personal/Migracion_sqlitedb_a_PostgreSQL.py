# Instala los paquetes necesarios
# pip install sqlalchemy psycopg2-binary openpyxl pandas

import sqlite3
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

# Conexión a SQLite
sqlite_conn = sqlite3.connect('database_consultas.db')

# Conexión a PostgreSQL (debes crear la BD primero)
pg_conn = create_engine('postgresql://usuario:contraseña@localhost/nombre_bd')

# Leer todas las tablas de SQLite
tablas = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", sqlite_conn)

# Migrar cada tabla
for tabla in tablas['name']:
    df = pd.read_sql(f'SELECT * FROM {tabla}', sqlite_conn)
    df.to_sql(tabla, pg_conn, if_exists='replace', index=False)

print("Migración completada")