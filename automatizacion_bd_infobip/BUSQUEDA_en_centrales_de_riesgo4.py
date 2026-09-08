import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os

# Configuración inicial
DB_PATH = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS\database_consultas.db"
EXPORT_FOLDER = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\Busquedas_Centrales_de_Riesgo_Enviadas"
engine = create_engine(f"sqlite:///{DB_PATH}")

# Crear carpeta de exportación si no existe
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def consultar_por_celular(numero_celular, exportar_excel=True):
    """
    Consulta registros por número celular manteniendo nombres originales de columnas
    y exporta números completos sin notación científica
    """
    try:
        print(f"\nConsultando registros para el celular: {numero_celular}")
        
        # Consulta SQL manteniendo nombres originales
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
        
        # Ejecutar consulta
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print("⚠ No se encontraron registros para este número")
            return None
        
        # Convertir columnas numéricas a strings para mantener todos los dígitos
        df['To'] = df['To'].astype('str')
        df['Message Id'] = df['Message Id'].astype('str')
        
        # Mostrar resumen
        print(f"\n📊 Resumen para {numero_celular}:")
        print(f"• Total registros: {len(df)}")
        print(f"• Primer envío: {df['Send At'].min()}")
        print(f"• Último envío: {df['Send At'].max()}")
        print(f"• Estados: {df['Status'].value_counts().to_dict()}")
        
        # Exportar a Excel
        if exportar_excel:
            fecha_hoy = datetime.now().strftime("%Y%m%d")
            archivo_excel = f"{numero_celular}_{fecha_hoy}.xlsx"
            ruta_completa = os.path.join(EXPORT_FOLDER, archivo_excel)
            
            # Exportar manteniendo nombres originales y formato de números
            df.to_excel(
                ruta_completa, 
                index=False, 
                engine='openpyxl'
            )
            
            print(f"\n✅ Datos exportados a:\n{ruta_completa}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error en la consulta: {str(e)}")
        return None

if __name__ == "__main__":
    # Solicitar número de celular
    numero = input("Ingrese el número celular a consultar (solo dígitos): ").strip()
    
    if numero.isdigit():
        resultado = consultar_por_celular(numero)
        
        # Mostrar vista previa si hay resultados
        if resultado is not None and not resultado.empty:
            print("\n🔍 Vista previa de los datos:")
            print(resultado[['To', 'Message Id', 'Status', 'Send At']].head(3))
    else:
        print("❌ El número debe contener solo dígitos")