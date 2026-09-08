import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date
from pathlib import Path
import openpyxl
from datetime import datetime, timedelta, time
import traceback  # Importación faltante añadida

# Configuración inicial
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Mayo_hasta2023_enero_xd.xlsx",
    "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto_xd.xlsx",
    "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero_xd.xlsx",
    "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero_xd.xlsx",
    "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre_xd.xlsx"
]
BD_NOMBRE = "database_consultas.db"

# 1. Crear motor de base de datos
engine = create_engine(f"sqlite:///{CARPETA/BD_NOMBRE}")
metadata = MetaData()

# Definición de la tabla con nombres consistentes
registros_table = Table(
    'registros', metadata,
    Column('ID', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('Periodo', Date),
    Column('To', Integer),
    Column('Message Id', Integer),
    Column('Send At', Date),
    Column('Hour At', String(8)),
    Column('Network Name', String(100)),
    Column('Status', String(50)),
    Column('Reason', String(100)),
    Column('Error Group', String(100)),
    Column('Error Name', String(100)),
    Column('Done At', Date),
    Column('Done Hour At', String(8)),
    Column('Text', Text)
)

# Crear la tabla si no existe
metadata.create_all(engine)

def normalizar_nombres(df):
    """Normaliza nombres de columnas y asegura compatibilidad con la tabla"""
    mapeo_nombres = {
        'Id': 'ID',
        'Message Id': 'Message Id',
        'Send At': 'Send At',
        'Hour At': 'Hour At',
        'Network Name': 'Network Name',
        'Error Group': 'Error Group',
        'Error Name': 'Error Name',
        'Done At': 'Done At',
        'Done Hour At': 'Done Hour At'
    }
    return df.rename(columns=mapeo_nombres)

def convertir_hora_str(valor):
    """Conversión segura a formato string HH:MM:SS o NULL"""
    try:
        if pd.isna(valor) or valor in ['', ' ', None, 'NULL', 'null', 'Null']:
            return None
            
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return None
                
            if ' ' in valor:
                valor = valor.split()[-1]
            
            if '.' in valor:
                valor = valor.split('.')[0]
                
            partes = valor.split(':')
            if len(partes) >= 2 and len(partes) <= 3:
                return f"{int(partes[0]):02d}:{int(partes[1]):02d}" + (f":{int(partes[2]):02d}" if len(partes) == 3 else ":00")
        
        if isinstance(valor, time):
            return valor.strftime('%H:%M:%S')
            
        if isinstance(valor, (int, float)):
            if valor < 1:
                hours = int(valor * 24)
                minutes = int((valor * 24 * 60) % 60)
                seconds = int((valor * 24 * 60 * 60) % 60)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
        return None
    except:
        return None

def importar_excel_grande(ruta_archivo):
    try:
        print(f"\nProcesando {ruta_archivo.name}...")
        
        try:
            columnas = pd.read_excel(ruta_archivo, nrows=0).columns.tolist()
            print("Columnas encontradas:", columnas)
        except Exception as e:
            print(f"🚨 Error al leer columnas: {str(e)}")
            return False

        try:
            wb = openpyxl.load_workbook(ruta_archivo, read_only=True)
            sheet = wb.active
            total_filas = sheet.max_row - 1
            wb.close()
            print(f"Total de filas a procesar: {total_filas}")
        except Exception as e:
            print(f"🚨 Error al calcular filas: {str(e)}")
            return False

        chunk_size = 100000
        for i in range(0, total_filas, chunk_size):
            try:
                print(f"Leyendo filas {i+1} a {min(i+chunk_size, total_filas)}...")
                
                df_chunk = pd.read_excel(
                    ruta_archivo,
                    skiprows=i+1,
                    nrows=chunk_size,
                    header=None,
                    names=columnas,
                    engine='openpyxl'
                )
                
                df_chunk = normalizar_nombres(df_chunk)
                
                if 'ID' in df_chunk.columns:
                    df_chunk = df_chunk.drop('ID', axis=1)
                
                date_cols = ['Periodo', 'Send_At', 'Done_At']
                time_cols = ['Hour_At', 'Done_Hour_At']
                
                for col in date_cols:
                    if col in df_chunk.columns:
                        df_chunk[col] = pd.to_datetime(df_chunk[col], errors='coerce').dt.date
                
                for col in time_cols:
                    if col in df_chunk.columns:
                        df_chunk[col] = df_chunk[col].apply(convertir_hora_str)
                        df_chunk[col] = df_chunk[col].replace(['', ' ', 'NULL', 'null'], None)
                
                df_chunk.to_sql(
                    'registros',
                    engine,
                    if_exists='append',
                    index=False,
                    dtype={
                        'Periodo': Date(),
                        'Send_At': Date(),
                        'Hour_At': String(8),
                        'Done_At': Date(),
                        'Done_Hour_At': String(8)
                    }
                )
                
            except Exception as e:
                print(f"⚠ Error en bloque {i//chunk_size + 1}: {str(e)}")
                print(traceback.format_exc())
                continue
        
        return True
    
    except Exception as e:
        print(f"🔥 Error crítico: {str(e)}")
        print(traceback.format_exc())
        return False

# Ejecutar el proceso
for archivo in ARCHIVOS_EXCEL:
    archivo_path = CARPETA / archivo
    if not archivo_path.exists():
        print(f"❌ Archivo no encontrado: {archivo}")
        continue
    
    if not importar_excel_grande(archivo_path):
        print(f"⚠ Error al procesar {archivo}")
    else:
        print(f"✅ {archivo} procesado correctamente")

# Verificación final
with engine.connect() as conn:
    print("\nVerificación de estructura de tabla:")
    resultado = conn.execute("PRAGMA table_info(registros)").fetchall()
    for col in resultado:
        print(f"Columna: {col[1]}, Tipo: {col[2]}, PK: {col[5]}, NotNull: {col[3]}")
    
    total = conn.execute("SELECT COUNT(*) FROM registros").scalar()
    print(f"\n{'='*50}\nProceso completado. Total registros: {total:,}")