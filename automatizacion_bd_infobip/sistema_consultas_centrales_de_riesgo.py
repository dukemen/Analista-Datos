import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import openpyxl
import os # Esto siempre funcionará en Python estándar - Propósito: Manejar rutas de archivos, directorios, variables de entorno, etc.

#este script lo que esta haciendo es crear una base de datos con cada uno de los registros de los 5 libros excel.
# Configuración - ¡AJUSTA ESTAS RUTAS! 
# Usamos Path(r"ruta") para evitar problemas con barras invertidas
CARPETA = Path(r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS")
ARCHIVOS_EXCEL = [
    "1_Consolidated_file_desde_2025_Abril_hasta2023_enero_xd.xlsx",  # Reemplaza con tus nombres reales
    "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto_xd.xlsx",
    "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero_xd.xlsx",
    "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero_xd.xlsx",
    "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre_xd.xlsx"
]
BD_NOMBRE = "database_consultas.db"

# Verificar que los archivos existan - Verificamos que cada archivo exista antes de procesarlo
for archivo in ARCHIVOS_EXCEL:
    if not (CARPETA/archivo).exists():
        print(f"❌ Error: No se encuentra {archivo} en {CARPETA}")
        exit()

# 1. Crear motor de base de datos
engine = create_engine(f"sqlite:///{CARPETA/BD_NOMBRE}")

# 2. Función optimizada para leer grandes Excels
def importar_excel_grande(ruta_archivo):
    try:
        print(f"\nProcesando {ruta_archivo.name}...")
        
        # Leer columnas
        columnas = pd.read_excel(ruta_archivo, nrows=0).columns.tolist()
        
        # Calcular total de filas
        wb = openpyxl.load_workbook(ruta_archivo, read_only=True)
        sheet = wb.active
        total_filas = sheet.max_row - 1  # Restamos el encabezado
        wb.close()
        
        # Procesar en bloques - Leemos en bloques de 100,000 registros
        chunk_size = 100000
        for i in range(0, total_filas, chunk_size):
            print(f"Leyendo filas {i+1} a {min(i+chunk_size, total_filas)}...")
            df_chunk = pd.read_excel(
                ruta_archivo,
                skiprows=i+1,
                nrows=chunk_size,
                header=None,
                names=columnas,
                engine='openpyxl'
            )
            df_chunk.to_sql('registros', engine, if_exists='append', index=False)
        
        return True
    
    except Exception as e:
        print(f"🚨 Error al procesar {ruta_archivo.name}: {str(e)}")
        return False

# 3. Procesar todos los archivos
for archivo in ARCHIVOS_EXCEL:
    if not importar_excel_grande(CARPETA/archivo):
        print(f"⚠ Saltando {archivo} debido a errores")
        continue

print("\n✅ Proceso completado. Base de datos creada en:", CARPETA/BD_NOMBRE)