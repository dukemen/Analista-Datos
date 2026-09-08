import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date, Time
from pathlib import Path
import openpyxl
from datetime import datetime, time, timedelta
import traceback

# Configuración inicial (ajusta tus rutas)
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Abril_hasta2023_enero_xd.xlsx",
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
    """Conversión robusta que maneja números enteros como horas y múltiples formatos"""
    try:
        # Si el valor es nulo o vacío
        if pd.isna(valor) or valor in ['', ' ', None, 'NULL', 0]:
            return None
            
        # Si es un número entero (como en tu ejemplo)
        if isinstance(valor, (int, float)):
            # Si es un número pequeño (1-24), tratarlo como hora
            if 0 <= valor <= 24:
                return time(int(valor), 0, 0)  # Convierte 5 → 05:00:00
            # Si es un número grande (timestamp de Excel)
            elif valor > 25569:  # Número de días desde 1900
                return (datetime(1900, 1, 1) + timedelta(days=valor-2)).time()
            return None
            
        # Si ya es un objeto time (no necesita conversión)
        if isinstance(valor, time):
            return valor
            
        # Si es un datetime (extraer solo la parte de tiempo)
        if isinstance(valor, datetime):
            return valor.time()
            
        # Si es un string (manejar múltiples formatos)
        if isinstance(valor, str):
            valor = valor.strip()
            
            # Formato HH:MM:SS
            if ':' in valor:
                parts = valor.split(':')
                if len(parts) == 3:  # HH:MM:SS
                    return time(int(parts[0]), int(parts[1]), int(parts[2]))
                elif len(parts) == 2:  # HH:MM
                    return time(int(parts[0]), int(parts[1]))
            
            # Formato timestamp completo (YYYY-MM-DD HH:MM:SS)
            try:
                return datetime.strptime(valor, '%Y-%m-%d %H:%M:%S').time()
            except ValueError:
                pass
                
            # Formato solo hora (HH:MM:SS)
            try:
                return datetime.strptime(valor, '%H:%M:%S').time()
            except ValueError:
                pass
                
        return None
    except Exception as e:
        print(f"⚠ Advertencia: No se pudo convertir {valor} a hora. Error: {str(e)}")
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
                
                # Leer chunk con tipos optimizados
                df_chunk = pd.read_excel(
                    ruta_archivo,
                    skiprows=i+1,
                    nrows=chunk_size,
                    header=None,
                    names=columnas,
                    engine='openpyxl',
                    dtype={
                        'Hour At': 'object',  # Leer como objeto para manejar múltiples formatos
                        'Done Hour At': 'object'
                    }
                )
                
                # Conversión segura de fechas y horas
                date_cols = ['Periodo', 'Send At', 'Done At']
                time_cols = ['Hour At', 'Done Hour At']
                
                for col in date_cols:
                    if col in df_chunk.columns:
                        df_chunk[col] = pd.to_datetime(df_chunk[col], errors='coerce').dt.date
                
                for col in time_cols:
                    if col in df_chunk.columns:
                        # Diagnóstico: mostrar muestra de valores antes de conversión
                        print(f"\nMuestra de valores en {col} antes de conversión:")
                        print(df_chunk[col].head())
                        
                        df_chunk[col] = df_chunk[col].apply(convertir_hora)
                        
                        # Diagnóstico: mostrar muestra de valores después de conversión
                        print(f"\nMuestra de valores en {col} después de conversión:")
                        print(df_chunk[col].head())
                
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
                    },
                    chunksize=10000  # Insertar en lotes para mejor rendimiento
                )
                
            except Exception as e:
                print(f"⚠ Error en bloque {i//chunk_size + 1}: {str(e)}")
                print(traceback.format_exc())  # Mostrar traceback completo
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
        print(f"⚠ No se pudo procesar completamente {archivo}")
    else:
        print(f"✅ {archivo} procesado correctamente")

# Mostrar estadísticas finales
with engine.connect() as conn:
    total_registros = conn.execute("SELECT COUNT(*) FROM registros").scalar()
    print(f"\n{'='*50}\nProceso completado. Total de registros en la base de datos: {total_registros:,}\n{'='*50}")