import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date
from pathlib import Path
import openpyxl
from datetime import datetime, time
import traceback

# ========== CONFIGURACIÓN INICIAL ==========
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Julio_hasta2023_enero_xd.xlsx",
    "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto_xd.xlsx",
    "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero_xd.xlsx",
    "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero_xd.xlsx",
    "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre_xd.xlsx"
]
BD_NOMBRE = "database_consultas.db"

# ========== CONEXIÓN A LA BASE DE DATOS ==========
engine = create_engine(f"sqlite:///{CARPETA/BD_NOMBRE}")
metadata = MetaData()

# ========== DEFINICIÓN DE LA TABLA (CON NOMBRES ORIGINALES) ==========
registros_table = Table(
    'registros', metadata,
    Column('ID', Integer, primary_key=True, autoincrement=True, nullable=False),
    Column('Periodo', Date),
    Column('To', Integer),
    Column('Message Id', Integer),  # Nombre original con espacio
    Column('Send At', Date),       # Nombre original con espacio
    Column('Hour At', String(8)),  # Nombre original con espacio (HH:MM:SS)
    Column('Network Name', String(100)),  # Nombre original
    Column('Status', String(50)),
    Column('Reason', String(100)),
    Column('Error Group', String(100)),   # Nombre original
    Column('Error Name', String(100)),    # Nombre original
    Column('Done At', Date),        # Nombre original
    Column('Done Hour At', String(8)),  # Nombre original
    Column('Text', Text)
)
metadata.create_all(engine)

# ========== FUNCIONES AUXILIARES ==========
def limpiar_hora(hora_str):
    """Convierte 'HH:MM:SS.microsegundos' a 'HH:MM:SS'"""
    if pd.isna(hora_str) or not hora_str:
        return None
    if isinstance(hora_str, str):
        return hora_str.split('.')[0]  # Elimina microsegundos
    if isinstance(hora_str, time):
        return hora_str.strftime('%H:%M:%S')
    return None

def procesar_fecha(fecha_str):
    """Convierte a date (sin hora)"""
    if pd.isna(fecha_str):
        return None
    try:
        return pd.to_datetime(fecha_str).date()
    except:
        return None

# ========== IMPORTACIÓN DE ARCHIVOS ==========
def importar_excel(ruta_archivo):
    try:
        print(f"\nProcesando: {ruta_archivo.name}")
        
        # Leer el archivo manteniendo nombres originales
        df = pd.read_excel(ruta_archivo, engine='openpyxl')
        
        # Eliminar columna Id si existe (para evitar conflictos con ID autoincremental)
        if 'Id' in df.columns:
            df.drop('Id', axis=1, inplace=True)
        
        # Procesar fechas y horas
        if 'Send At' in df.columns:
            df['Send At'] = df['Send At'].apply(procesar_fecha)
        if 'Done At' in df.columns:
            df['Done At'] = df['Done At'].apply(procesar_fecha)
        if 'Hour At' in df.columns:
            df['Hour At'] = df['Hour At'].apply(limpiar_hora)
        if 'Done Hour At' in df.columns:
            df['Done Hour At'] = df['Done Hour At'].apply(limpiar_hora)
        
        # Insertar en SQLite manteniendo nombres originales
        df.to_sql(
            'registros',
            engine,
            if_exists='append',
            index=False,
            dtype={
                'Periodo': Date(),
                'Send At': Date(),
                'Hour At': String(8),
                'Done At': Date(),
                'Done Hour At': String(8)
            }
        )
        
        print(f"✅ Registros insertados: {len(df):,}")
        return True
        
    except Exception as e:
        print(f"❌ Error en {ruta_archivo.name}: {str(e)}")
        print(traceback.format_exc())
        return False

# ========== EJECUCIÓN PRINCIPAL ==========
if __name__ == "__main__":
    for archivo in ARCHIVOS_EXCEL:
        archivo_path = CARPETA / archivo
        if archivo_path.exists():
            importar_excel(archivo_path)
        else:
            print(f"⚠ Archivo no encontrado: {archivo}")
    
    # Verificación final
    with engine.connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM registros").scalar()
        print(f"\n{'='*50}\nTOTAL REGISTROS IMPORTADOS: {total:,}")
