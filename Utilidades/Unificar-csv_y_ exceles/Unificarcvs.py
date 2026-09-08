import pandas as pd
import glob
import os
from tkinter import Tk, filedialog

# 1. Configurar la ventana para seleccionar carpeta
root = Tk()
root.withdraw()  # Oculta la ventana principal
root.attributes('-topmost', True)  # Trae la ventana al frente

# 2. Pedir al usuario que seleccione la carpeta con los CSVs
print("👉 Por favor, selecciona la carpeta donde están tus archivos CSV...")
carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los archivos CSV")

if not carpeta:
    print("❌ No se seleccionó ninguna carpeta. Saliendo...")
    exit()

# 3. Buscar archivos CSV en la carpeta seleccionada
archivos_csv = glob.glob(os.path.join(carpeta, '*.csv'))

if not archivos_csv:
    print(f"❌ No se encontraron archivos CSV en: {carpeta}")
    exit()

print(f"📂 Archivos encontrados ({len(archivos_csv)}):")
for archivo in archivos_csv:
    print(f" - {os.path.basename(archivo)}")

# 4. Combinar todos los CSVs
try:
    df_combinado = pd.concat([pd.read_csv(archivo) for archivo in archivos_csv], ignore_index=True)
    
    # 5. Guardar el resultado en la misma carpeta
    ruta_salida = os.path.join(carpeta, 'archivo_combinado.csv')
    df_combinado.to_csv(ruta_salida, index=False, encoding='utf-8')
    
    print(f"✅ ¡Archivos combinados con éxito! Guardado en:\n{ruta_salida}")

except Exception as e:
    print(f"❌ Error al combinar archivos: {e}")