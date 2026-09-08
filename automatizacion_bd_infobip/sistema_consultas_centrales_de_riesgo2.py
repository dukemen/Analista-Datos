import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date, Time
from pathlib import Path
import openpyxl
from datetime import datetime

# Configuración inicial
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Abril_hasta2023_enero_xd.xlsx",  # Reemplaza con tus nombres reales
    "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto_xd.xlsx",
    "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero_xd.xlsx",
    "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero_xd.xlsx",
    "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre_xd.xlsx"
]
BD_NOMBRE = "database_consultas.db"

# 1. Crear motor de base de datos y definir estructura de tabla exacta
engine = create_engine(f"sqlite:///{CARPETA/BD_NOMBRE}")
metadata = MetaData()

# Definición exacta de la tabla según especificación
Table(
    'registros', metadata,
    Column('ID', Integer, primary_key=True, autoincrement=True),  # ID auto-incremental
    Column('Periodo', Date),                # Tipo DATE
    Column('To', Integer),                  # Integer sin tamaño específico (SQLite ignora el tamaño)
    Column('Message Id', Integer),          # Integer sin tamaño específico
    Column('Send At', Date),                # Tipo DATE
    Column('Hour At', Time),                # Tipo TIME
    Column('Network Name', String(100)),    # String con longitud 100
    Column('Status', String(50)),           # String con longitud 50
    Column('Reason', String(100)),          # String con longitud 100
    Column('Error Group', String(100)),     # String con longitud 100
    Column('Error Name', String(100)),      # String con longitud 100
    Column('Done At', Date),                # Tipo DATE
    Column('Done Hour At', Time),           # Tipo TIME
    Column('Text', Text)                    # Tipo TEXT para contenido largo
)

# Crear la tabla si no existe
metadata.create_all(engine)

def importar_excel_grande(ruta_archivo):
    try:
        print(f"\nProcesando {ruta_archivo.name}...")
        
        # 1. Verificar tipo de archivo
        if ruta_archivo.suffix.lower() not in ['.xlsx', '.xls']:
            print(f"⚠ Formato no soportado: {ruta_archivo.suffix}")
            return False
        
        # 2. Leer columnas
        try:
            # Leer solo los nombres de columnas
            columnas = pd.read_excel(ruta_archivo, nrows=0).columns.tolist()
            print("Columnas encontradas:", columnas)
        except Exception as e:
            print(f"🚨 Error al leer columnas: {str(e)}")
            return False
        
        # 3. Calcular total de filas
        try:
            wb = openpyxl.load_workbook(ruta_archivo, read_only=True)
            sheet = wb.active
            total_filas = sheet.max_row - 1  # Restar el encabezado
            wb.close()
            print(f"Total de filas a procesar: {total_filas}")
        except Exception as e:
            print(f"🚨 Error al calcular filas: {str(e)}")
            return False
        
        # 4. Procesar en bloques
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
                
                # Convertir a los tipos de datos especificados
                if 'Periodo' in df_chunk.columns:
                    df_chunk['Periodo'] = pd.to_datetime(df_chunk['Periodo']).dt.date
                
                if 'Send At' in df_chunk.columns:
                    df_chunk['Send At'] = pd.to_datetime(df_chunk['Send At']).dt.date
                
                if 'Hour At' in df_chunk.columns:
                    df_chunk['Hour At'] = pd.to_datetime(df_chunk['Hour At']).dt.time
                
                if 'Done At' in df_chunk.columns:
                    df_chunk['Done At'] = pd.to_datetime(df_chunk['Done At']).dt.date
                
                if 'Done Hour At' in df_chunk.columns:
                    df_chunk['Done Hour At'] = pd.to_datetime(df_chunk['Done Hour At']).dt.time
                
                # Convertir columnas numéricas
                if 'To' in df_chunk.columns:
                    df_chunk['To'] = pd.to_numeric(df_chunk['To'], errors='coerce').fillna(0).astype('int64')
                
                if 'Message Id' in df_chunk.columns:
                    df_chunk['Message Id'] = pd.to_numeric(df_chunk['Message Id'], errors='coerce').fillna(0).astype('int64')
                
                # Insertar en BD (ignorando el índice)
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

# Procesar todos los archivos
for archivo in ARCHIVOS_EXCEL:
    archivo_path = CARPETA / archivo
    if not archivo_path.exists():
        print(f"❌ Archivo no encontrado: {archivo}")
        continue
    
    if not importar_excel_grande(archivo_path):
        print(f"⚠ No se pudo procesar completamente {archivo}")
    else:
        print(f"✅ {archivo} procesado correctamente")

print("\nProceso completado. Base de datos creada en:", CARPETA/BD_NOMBRE)