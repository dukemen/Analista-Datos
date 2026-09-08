import pandas as pd
import glob
import os
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo

# Configuración inicial
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
        showinfo("Información", "No se pudo procesar ningún archivo.")
        return
    
    # Unificar todos los DataFrames
    df_unificado = pd.concat(dfs, ignore_index=True)
    
    # Guardar el resultado en la misma carpeta seleccionada
    output_path = os.path.join(input_folder, output_file)
    df_unificado.to_excel(output_path, index=False)
    
    mensaje = f"¡Proceso completado!\n\nSe han unificado {len(dfs)} archivos.\n\nArchivo resultante guardado en:\n{output_path}"
    print(f"\n{mensaje}")
    showinfo("Proceso completado", mensaje)

if __name__ == "__main__":
    unificar_archivos()


    """
    Cambios realizados:
Selección de carpeta interactiva:

Ahora aparecerá una ventana para que selecciones la carpeta donde están los archivos

No necesitas modificar el código para cambiar la ubicación

Mejoras en la interfaz:

Mensajes de información en ventanas emergentes

Confirmación cuando el proceso termina

Muestra la ruta completa donde se guardó el archivo unificado

Guardado automático:

El archivo resultante se guardará en la misma carpeta que seleccionaste

Instrucciones de uso:
Ejecuta el script como antes

Se abrirá una ventana para que selecciones la carpeta con los archivos

El programa procesará los archivos y mostrará mensajes de progreso

Al finalizar, te mostrará dónde quedó guardado el archivo unificado con todas la colunmas, en el unificarexcel3 solamente me trae las columnas que necesito.

"""
