import pandas as pd
import glob
import os
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo

# Configuración inicial
output_file = 'reporte_unificado.xlsx'  # Nombre del archivo de salida

# Columnas a extraer (las que especificaste)
columnas_a_extraer = [
    "To", "Message Id", "Send At", "Network Name", "Status", 
    "Reason", "Error Group", "Error Name", "Done At", "Text"
]

def seleccionar_carpeta():
    """Muestra un diálogo para seleccionar la carpeta con los archivos"""
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal
    root.attributes('-topmost', True)  # Traer al frente
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los archivos Excel a unificar")
    root.destroy()
    return carpeta

def unificar_archivos():
    # Seleccionar carpeta
    input_folder = seleccionar_carpeta()
    
    if not input_folder:
        print("No se seleccionó ninguna carpeta. Operación cancelada.")
        return
    
    print(f"\nProcesando archivos en: {input_folder}")
    
    # Buscar todos los archivos Excel que coincidan con el patrón
    archivos = glob.glob(os.path.join(input_folder, '*_Reporte_Centrales_*.xlsx'))
    
    if not archivos:
        showinfo("Información", "No se encontraron archivos para unificar en la carpeta seleccionada.")
        return
    
    print(f"Se encontraron {len(archivos)} archivos para procesar:")
    for archivo in archivos:
        print(f"- {os.path.basename(archivo)}")
    
    # Lista para almacenar los DataFrames
    dfs = []
    
    for archivo in archivos:
        try:
            # Leer el archivo Excel conservando formatos
            df = pd.read_excel(archivo, dtype={'To': str})  # Forzar 'To' como texto para conservar formato
            
            # Verificar que tenga las columnas necesarias
            columnas_faltantes = [col for col in columnas_a_extraer if col not in df.columns]
            if columnas_faltantes:
                print(f"Advertencia: El archivo {os.path.basename(archivo)} no tiene las columnas: {', '.join(columnas_faltantes)}. Se omitirá.")
                continue
                
            # Seleccionar solo las columnas requeridas
            df = df[columnas_a_extraer]
            
            # Convertir columnas de fecha si existen
            for col in ['Send At', 'Done At']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col])
            
            # Conservar Message Id como texto si es numérico
            if 'Message Id' in df.columns and pd.api.types.is_numeric_dtype(df['Message Id']):
                df['Message Id'] = df['Message Id'].astype(str)
            
            # Agregar una columna con el nombre del archivo origen
            df['Archivo_Origen'] = os.path.basename(archivo)
            
            dfs.append(df)
            
        except Exception as e:
            print(f"Error al procesar {os.path.basename(archivo)}: {str(e)}")
            continue
    
    if not dfs:
        showinfo("Información", "No se pudo procesar ningún archivo.")
        return
    
    # Unificar todos los DataFrames
    df_unificado = pd.concat(dfs, ignore_index=True)
    
    # Guardar el resultado conservando formatos
    output_path = os.path.join(input_folder, output_file)
    
    with pd.ExcelWriter(output_path, engine='xlsxwriter', datetime_format='dd/mm/yyyy hh:mm:ss') as writer:
        df_unificado.to_excel(writer, index=False)
        
        # Ajustar el ancho de las columnas automáticamente
        worksheet = writer.sheets['Sheet1']
        for i, col in enumerate(df_unificado.columns):
            column_len = max(df_unificado[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
    
    mensaje = f"¡Proceso completado!\n\nSe han unificado {len(dfs)} archivos.\n\nColumnas incluidas:\n{', '.join(columnas_a_extraer)}\n\nArchivo resultante guardado en:\n{output_path}"
    print(f"\n{mensaje}")
    showinfo("Proceso completado", mensaje)

if __name__ == "__main__":
    unificar_archivos()

    """

    Cambios realizados:
Selección específica de columnas:

Ahora solo extrae las columnas que especificaste: To, Message Id, Send At, Network Name, Status, Reason, Error Group, Error Name, Done At, Text

Conservación de formatos:

Campo "To": Se fuerza como texto para conservar números largos (como números de teléfono)

Campos de fecha/hora ("Send At", "Done At"): Se convierten explícitamente a datetime y se guardan con formato

"Message Id": Se conserva como texto si es numérico para evitar notación científica

Mejoras en el Excel resultante:

Formato de fecha/hora consistente (dd/mm/yyyy hh:mm:ss)

Ajuste automático del ancho de columnas

Se mantiene la columna "Archivo_Origen" para rastreabilidad

Instrucciones adicionales:
El script sigue funcionando igual: seleccionas la carpeta y procesa los archivos

El archivo resultante tendrá solo las columnas solicitadas

Los formatos originales de números y fechas se conservarán correctamente, solamente debes corregir el formato de la fecha y hora,
 debe ser dd/mm/yyyy hh:mm:ss y me esta saliendo  mm/dd/yyyy hh:mm:ss
"""