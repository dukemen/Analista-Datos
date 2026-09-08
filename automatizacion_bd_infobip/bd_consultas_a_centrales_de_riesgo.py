import pandas as pd
from pathlib import Path

# 1. Definir la ruta de la carpeta (cambia "TU_USUARIO" por tu usuario de Windows)
carpeta = Path("C:/Users/PCSISTEMAS/Documents\TRABAJOS_PYTHON")

#/////////////////////////////////////Paso 1: Leer los 5 archivos Excel\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
# Lista de rutas de tus archivos Excel
archivos_excel = [


    carpeta / "1_Consolidated_file_desde_2025_Abril_hasta2023_enero.xlsx",
    carpeta / "2_Consolidated_file_desde_2022_Diciembre_hasta2021_Agosto.xlsx",
    carpeta / "3_Consolidated_file_desde_2021_Julio_hasta2020_Enero.xlsx",
    carpeta / "4_Consolidated_file_desde_2019_Diciembre_hasta2018_Enero.xlsx",
    carpeta / "5_Consolidated_file_desde_2017_Diciembre_hasta2016_Noviembre.xlsx"
]


# 3. Leer y unir todos los archivos
datos_completos = pd.concat([pd.read_excel(archivo) for archivo in archivos])

# 4. Guardar el resultado (en la misma carpeta)
datos_completos.to_excel(carpeta / "DATOS_FINALES.xlsx", index=False)

print("¡Archivos unidos correctamente! Revisa DATOS_FINALES.xlsx")


# Leer todos los archivos y almacenarlos en una lista de DataFrames
#dataframes = [pd.read_excel(archivo) for archivo in archivos_excel]

# Opción para archivos muy grandes (lectura por chunks) Si algún archivo es extremadamente grande (>500k filas), usa chunksize:

'''
chunks = []
for archivo in archivos_excel:
    for chunk in pd.read_excel(archivo, chunksize=100000):  # Lee de 100k en 100k filas
        chunks.append(chunk)
dataframes = chunks
'''


#/////////////////////////////////////Paso 2: Unificar todos los DataFrames en uno solo\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
# Unificar todos los DataFrames
#df_final = pd.concat(dataframes, ignore_index=True)

# Eliminar duplicados (si es necesario)
#df_final = df_final.drop_duplicates()



#/////////////////////////////////////Paso 3: Optimizar el DataFrame (reducir memoria)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
# Optimizar tipos de datos para ahorrar memoria
def optimizar_tipos(df):
    for col in df.columns:
        if df[col].dtype == "object":
            # Convertir cadenas a 'category' si hay repeticiones
            if df[col].nunique() / len(df[col]) < 0.5:
                df[col] = df[col].astype("category")
        elif "int" in str(df[col].dtype):
            # Reducir enteros al mínimo necesario
            df[col] = pd.to_numeric(df[col], downcast="integer")
        elif "float" in str(df[col].dtype):
            # Reducir floats
            df[col] = pd.to_numeric(df[col], downcast="float")
    return df

df_final = optimizar_tipos(df_final)


#/////////////////////////////////////Paso 4: Guardar en un nuevo Excel (o Parquet para mayor eficiencia)\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
#Opción 1: Guardar en Excel (para descarga)
df_final.to_excel("datos_unificados.xlsx", index=False, engine="openpyxl")

#Opción 2: Guardar en Parquet (más eficiente para consultas)
#df_final.to_parquet("datos_unificados.parquet")