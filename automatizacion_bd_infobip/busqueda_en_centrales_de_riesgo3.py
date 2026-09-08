import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os

# Configuración inicial
DB_PATH = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS\database_consultas.db"
EXPORT_FOLDER = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\Busquedas_Centrales_de_Riesgo_Enviadas"
engine = create_engine(f"sqlite:///{DB_PATH}")

# Asegurar que la carpeta de exportación exista
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def consultar_por_celular(numero_celular, exportar_excel=True):
    try:
        print(f"\nConsultando registros para el celular: {numero_celular}")
        
        query = f"""
        SELECT 
            [Periodo],
            [To],
            [Message Id],
            [Send At],
            [Hour At],
            [Network Name],
            [Status],
            [Reason],
            [Error Group],
            [Error Name],
            [Done At],
            [Done Hour At],
            [Text]
        FROM registros
        WHERE [To] = {numero_celular}
        ORDER BY [Send At] DESC
        """
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("⚠ No se encontraron registros para este número")
            return None
        
        # Convertir columnas numéricas a enteros
        df['To'] = df['To'].astype('int64')
        df['Message Id'] = df['Message Id'].astype('int64')
        
        print(f"\n📊 Resumen para {numero_celular}:")
        print(f"• Total registros: {len(df)}")
        print(f"• Primer envío: {df['Send At'].min()}")
        print(f"• Último envío: {df['Send At'].max()}")
        print(f"• Estados: {df['Status'].value_counts().to_dict()}")
        
        if exportar_excel:
            fecha_hoy = datetime.now().strftime("%Y%m%d")
            archivo_excel = f"{numero_celular}_{fecha_hoy}.xlsx"
            ruta_completa = os.path.join(EXPORT_FOLDER, archivo_excel)
            
            # Crear un ExcelWriter para personalizar el formato
            with pd.ExcelWriter(ruta_completa, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
                
                # Acceder al libro y hojas de trabajo
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                
                # Formato de número entero sin decimales
                num_format = workbook.add_format({'num_format': '0'})
                
                # Aplicar formato a las columnas
                worksheet.set_column('B:B', 15, num_format)  # Columna Celular
                worksheet.set_column('C:C', 20, num_format)  # Columna Message Id
            
            print(f"\n✅ Datos exportados a:\n{ruta_completa}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error en la consulta: {str(e)}")
        return None

if __name__ == "__main__":
    numero = input("Ingrese el número celular a consultar (solo dígitos): ").strip()
    
    if numero.isdigit():
        resultado = consultar_por_celular(numero)
        
        if resultado is not None and not resultado.empty:
            print("\n🔍 Vista previa de los datos:")
            print(resultado.head(3))
    else:
        print("❌ El número debe contener solo dígitos")
