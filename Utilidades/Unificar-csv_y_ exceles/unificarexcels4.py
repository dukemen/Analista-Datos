import pandas as pd
import glob
import os
from tkinter import Tk, filedialog
from tkinter.messagebox import showinfo
from datetime import datetime

# Configuración inicial
output_file = 'reporte_unificado.xlsx'  # Nombre del archivo de salida

# --- NUEVO MENSAJE AL INICIO ---
def mostrar_mensaje_inicial():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showwarning("Precaución", 
                         "Por favor cierre el archivo 'reporte_unificado.xlsx' si está abierto\n\n"
                         "El proceso no podrá continuar si el archivo está en uso.")
    root.destroy()

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

def formatear_fecha(fecha):
    """Formatea datetime a string con el formato dd/mm/yyyy hh:mm:ss"""
    if pd.isna(fecha):
        return ""
    return fecha.strftime('%d/%m/%Y %H:%M:%S')

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
            df = pd.read_excel(archivo, dtype={'To': str})
            
            # Verificar que tenga las columnas necesarias
            columnas_faltantes = [col for col in columnas_a_extraer if col not in df.columns]
            if columnas_faltantes:
                print(f"Advertencia: El archivo {os.path.basename(archivo)} no tiene las columnas: {', '.join(columnas_faltantes)}. Se omitirá.")
                continue
                
            # Seleccionar solo las columnas requeridas
            df = df[columnas_a_extraer]
            
            # Convertir y formatear columnas de fecha
            for col in ['Send At', 'Done At']:
                if col in df.columns:
                    # Convertir a datetime
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    # Formatear como string con el formato deseado
                    df[col] = df[col].apply(formatear_fecha)
            
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
    
    # Agregar las columnas vacías al principio
    df_unificado.insert(0, 'Id', '')
    df_unificado.insert(1, 'Periodo', '')
    
    # Guardar el resultado
    output_path = os.path.join(input_folder, output_file)
    
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df_unificado.to_excel(writer, index=False)
        
        # Obtener el objeto workbook y worksheet para formato adicional
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Formato para columnas de texto
        text_format = workbook.add_format({'num_format': '@'})
        
        # Ajustar el ancho de las columnas automáticamente
        for i, col in enumerate(df_unificado.columns):
            column_len = max(df_unificado[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
        
        # Aplicar formato de texto a columnas importantes
        worksheet.set_column('A:A', 15, text_format)  # Columna Id
        worksheet.set_column('B:B', 15, text_format)  # Columna Periodo
        worksheet.set_column('C:C', 20, text_format)  # Columna To (para números largos)
    
    mensaje = f"¡Proceso completado!\n\nSe han unificado {len(dfs)} archivos.\n\nColumnas agregadas:\n- Id (vacía)\n- Periodo (vacía)\n\nFormato de fechas: dd/mm/yyyy hh:mm:ss\n\nArchivo resultante guardado en:\n{output_path}"
    print(f"\n{mensaje}")
    showinfo("Proceso completado", mensaje)

if __name__ == "__main__":
    unificar_archivos()