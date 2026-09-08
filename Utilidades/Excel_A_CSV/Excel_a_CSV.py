import pandas as pd
from tkinter import Tk, filedialog
import os

# Configuración inicial
print("=== Conversor de Excel a CSV ===")

# 1. Abrir ventana para seleccionar archivo Excel
root = Tk()
root.withdraw()  # Oculta la ventana principal
file_path = filedialog.askopenfilename(
    title="Selecciona el archivo Excel",
    filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
)

if not file_path:
    print("No se seleccionó ningún archivo. Saliendo...")
    exit()

# 2. Leer el archivo Excel (usando openpyxl como motor)
try:
    df = pd.read_excel(file_path, engine='openpyxl')  # Asegura compatibilidad
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

# 3. Generar ruta de salida (misma carpeta, extensión .csv)
output_dir = os.path.dirname(file_path)
output_filename = os.path.splitext(os.path.basename(file_path))[0] + ".csv"
output_path = os.path.join(output_dir, output_filename)

# 4. Guardar como CSV (UTF-8, separado por comas)
try:
    df.to_csv(output_path, index=False, encoding='utf-8', sep=',')
    print(f"¡Archivo convertido con éxito!\nRuta: {output_path}")
except Exception as e:
    print(f"Error al guardar el CSV: {e}")

# 5. Verificación rápida de caracteres especiales
print("\nVerificación de primeras filas:")
print(df.head())  # Muestra las primeras filas para revisar caracteres