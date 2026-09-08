import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os

# Configuración
DB_PATH = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS\database_consultas.db"
EXPORT_FOLDER = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\Busquedas_Centrales_de_Riesgo_Enviadas"
engine = create_engine(f"sqlite:///{DB_PATH}")
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def consultar_por_celular(numero_celular):
    """Consulta y exporta manteniendo números como texto exacto"""
    try:
        print(f"\nConsultando registros para: {numero_celular}")
        
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
            print("⚠ No se encontraron registros")
            return None

        # Convertir a texto (manteniendo ceros iniciales si los hay)
        df['To'] = df['To'].astype(str)
        df['Message Id'] = df['Message Id'].astype(str)
        
        # Exportar con formato de texto
        fecha = datetime.now().strftime("%Y%m%d")
        archivo = os.path.join(EXPORT_FOLDER, f"consulta_{numero_celular}_{fecha}.xlsx")
        
        with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
            # Forzar formato de texto en Excel
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Aplicar formato "@" (texto) a las columnas B (To) y C (Message Id)
            for col in ['B', 'C']:
                for row in range(2, len(df)+2):  # Fila 2 en adelante (fila 1 es encabezado)
                    worksheet[f'{col}{row}'].number_format = '@'  # Formato texto
        
        print(f"\n✅ Exportado a: {archivo}")
        print("🔍 Vista previa:")
        print(df[['To', 'Message Id', 'Status', 'Send At']].head(3))
        
        return df
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    numero = input("Ingrese número celular (solo dígitos): ").strip()
    if numero.isdigit():
        consultar_por_celular(numero)
    else:
        print("❌ Solo dígitos permitidos")