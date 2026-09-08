import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date, Time
from pathlib import Path
import openpyxl
from datetime import datetime

# Configuración inicial (ajusta tus rutas)
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Abril_hasta2023_enero_xd.xlsx",  # Reemplaza con tus nombres reales
    "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto_xd.xlsx",
    "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero_xd.xlsx",
    "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero_xd.xlsx",
    "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre_xd.xlsx"
]
BD_NOMBRE = "database_consultas.db"

# 1. Crear motor de base de datos
engine = create_engine(f"sqlite:///{CARPETA/BD_NOMBRE}")
metadata = MetaData()

# Definición exacta de la tabla según especificación
Table(
    'registros', metadata,
    Column('ID', Integer, primary_key=True, autoincrement=True),
    Column('Periodo', Date),
    Column('To', Integer),
    Column('Message Id', Integer),
    Column('Send At', Date),
    Column('Hour At', Time),
    Column('Network Name', String(100)),
    Column('Status', String(50)),
    Column('Reason', String(100)),
    Column('Error Group', String(100)),
    Column('Error Name', String(100)),
    Column('Done At', Date),
    Column('Done Hour At', Time),
    Column('Text', Text)
)

# Crear la tabla si no existe
metadata.create_all(engine)

def normalizar_nombres(df):
    """Asegura que los nombres de columnas coincidan exactamente con la tabla"""
    mapeo_nombres = {
        # Si hay diferencias entre Excel y la tabla, definirlas aquí
        # Ejemplo: 'Message_Id': 'Message Id'
    }
    return df.rename(columns=mapeo_nombres)

def convertir_hora(valor):
    """Conversión segura a formato time"""
    try:
        if pd.isna(valor):
            return None
        if isinstance(valor, str):
            if ':' in valor:  # Formato HH:MM:SS
                return datetime.strptime(valor.split()[-1], '%H:%M:%S').time()
            return datetime.strptime(valor, '%H:%M:%S').time()
        if isinstance(valor, datetime):
            return valor.time()
        return None
    except:
        return None

def importar_excel_grande(ruta_archivo):
    try:
        print(f"\nProcesando {ruta_archivo.name}...")
        
        # Leer estructura del archivo
        try:
            columnas = pd.read_excel(ruta_archivo, nrows=0).columns.tolist()
            print("Columnas encontradas:", columnas)
        except Exception as e:
            print(f"🚨 Error al leer columnas: {str(e)}")
            return False

        # Calcular total de filas
        try:
            wb = openpyxl.load_workbook(ruta_archivo, read_only=True)
            sheet = wb.active
            total_filas = sheet.max_row - 1
            wb.close()
            print(f"Total de filas a procesar: {total_filas}")
        except Exception as e:
            print(f"🚨 Error al calcular filas: {str(e)}")
            return False

        # Procesar en bloques
        chunk_size = 100000
        for i in range(0, total_filas, chunk_size):
            try:
                print(f"Leyendo filas {i+1} a {min(i+chunk_size, total_filas)}...")
                
                # Leer chunk
                df_chunk = pd.read_excel(
                    ruta_archivo,
                    skiprows=i+1,
                    nrows=chunk_size,
                    header=None,
                    names=columnas,
                    engine='openpyxl'
                )
                
                # Conversión segura de fechas y horas
                date_cols = ['Periodo', 'Send At', 'Done At']
                time_cols = ['Hour At', 'Done Hour At']
                
                for col in date_cols:
                    if col in df_chunk.columns:
                        df_chunk[col] = pd.to_datetime(df_chunk[col], errors='coerce').dt.date
                
                for col in time_cols:
                    if col in df_chunk.columns:
                        df_chunk[col] = df_chunk[col].apply(convertir_hora)
                
                # Insertar en BD
                df_chunk.to_sql(
                    'registros',
                    engine,
                    if_exists='append',
                    index=False,
                    dtype={
                        'Periodo': Date(),
                        'Send At': Date(),
                        'Hour At': Time(),
                        'Done At': Date(),
                        'Done Hour At': Time()
                    }
                )
                
            except Exception as e:
                print(f"⚠ Error en bloque {i//chunk_size + 1}: {str(e)}")
                continue
        
        return True
    
    except Exception as e:
        print(f"🔥 Error crítico: {str(e)}")
        return False

# Ejecutar el proceso
for archivo in ARCHIVOS_EXCEL:
    archivo_path = CARPETA / archivo
    if not importar_excel_grande(archivo_path):
        print(f"⚠ Error al procesar {archivo}")
    else:
        print(f"✅ {archivo} procesado correctamente")