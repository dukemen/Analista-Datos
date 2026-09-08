import pandas as pd
import glob
import os

# Configuración inicial
input_folder = '.'  # Carpeta donde están los archivos (actual por defecto)
output_file = 'reporte_unificado.xlsx'  # Nombre del archivo de salida

# Columnas esperadas (las que proporcionaste)
columnas_esperadas = [
    "Account Name", "Traffic Source", "Communication Name", "Communication Scheduled For",
    "Communication Start Date", "Communication Template", "From", "To", "Message Id",
    "Send At", "Country Prefix", "Country Name", "Network Name", "Original MCC",
    "Original MNC", "Original MCC MNC", "Purchase Price", "Message Type", "SMS Type",
    "Status", "Reason", "Action", "Error Group", "Error Name", "Done At", "Text",
    "Message Length", "Messages Count", "Service Name", "User Name", "Paired Message Id",
    "Clicks", "Verified", "Data Payload", "Bulk Id", "Campaign Reference",
    "Application ID", "Entity ID"
]

def unificar_archivos():
    # Buscar todos los archivos Excel que coincidan con el patrón
    archivos = glob.glob(os.path.join(input_folder, '*_Reporte_Centrales_*.xlsx'))
    
    if not archivos:
        print("No se encontraron archivos para unificar.")
        return
    
    print(f"Se encontraron {len(archivos)} archivos para procesar:")
    for archivo in archivos:
        print(f"- {os.path.basename(archivo)}")
    
    # Lista para almacenar los DataFrames
    dfs = []
    
    for archivo in archivos:
        try:
            # Leer el archivo Excel
            df = pd.read_excel(archivo)
            
            # Verificar que tenga las columnas esperadas
            if not all(col in df.columns for col in columnas_esperadas):
                print(f"Advertencia: El archivo {os.path.basename(archivo)} no tiene todas las columnas esperadas. Se omitirá.")
                continue
                
            # Ordenar las columnas según el orden esperado
            df = df[columnas_esperadas]
            
            # Agregar una columna con el nombre del archivo origen
            df['Archivo_Origen'] = os.path.basename(archivo)
            
            dfs.append(df)
            
        except Exception as e:
            print(f"Error al procesar {os.path.basename(archivo)}: {str(e)}")
            continue
    
    if not dfs:
        print("No se pudo procesar ningún archivo.")
        return
    
    # Unificar todos los DataFrames
    df_unificado = pd.concat(dfs, ignore_index=True)
    
    # Guardar el resultado
    df_unificado.to_excel(output_file, index=False)
    print(f"\n¡Proceso completado! Se han unificado {len(dfs)} archivos en '{output_file}'.")

if __name__ == "__main__":
    unificar_archivos()


    # Instrucciones de Uso
    #  Guarda este script en un archivo .py (por ejemplo, unificar_excel.py) en la misma carpeta donde están tus archivos Excel.
    # Ejecuta el script con Python, su visual studio code
    # El script: Buscará automáticamente todos los archivos que coincidan con el patrón *_Reporte_Centrales_*.xlsx
    # Verificará que tengan las columnas correctas
    # Los combinará en un solo archivo llamado reporte_unificado.xlsx
    # Agregará una columna adicional llamada Archivo_Origen para saber de qué archivo proviene cada registro
    # Personalización Si necesitas ajustar algo:
    # Cambia input_folder si los archivos están en otra carpeta
    # Modifica output_file para cambiar el nombre del archivo de salida
    # Ajusta columnas_esperadas si hay cambios en la estructura