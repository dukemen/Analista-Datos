#\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\Consultar por celular////////////////////////////////////////////

import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# 1. Configuración inicial
DB_PATH = r"C:\Users\PCSISTEMAS\Documents\INFOBIP\PY_CONSULTAS_CENTRALES_RIESGO\COPIAS\database_consultas.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

# 2. Función para consultar por número celular
def consultar_por_celular(numero_celular, exportar_excel=True):
    """
    Consulta registros por número celular y opcionalmente exporta a Excel
    
    Args:
        numero_celular (str/int): Número a buscar (en columna 'To')
        exportar_excel (bool): Si True, exporta resultados a Excel
    """
    try:
        print(f"\nConsultando registros para el celular: {numero_celular}")
        
        # Consulta SQL optimizada
        query = f"""
        SELECT 
            [Periodo],
            [To] as Celular,
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
        
        # Mostrar resumen visual
        print(f"\n📊 Resumen para {numero_celular}:")
        print(f"• Total registros: {len(df)}")
        print(f"• Primer envío: {df['Send At'].min()}")
        print(f"• Último envío: {df['Send At'].max()}")
        print(f"• Estados: {df['Status'].value_counts().to_dict()}")
        
        # Exportar a Excel si se solicita
        if exportar_excel:
            fecha_hoy = datetime.now().strftime("%Y%m%d")
            archivo_excel = f"consulta_celular_{numero_celular}_{fecha_hoy}.xlsx"
            df.to_excel(archivo_excel, index=False)
            print(f"\n✅ Datos exportados a: {archivo_excel}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error en la consulta: {str(e)}")
        return None

# 3. Ejemplo de uso
if __name__ == "__main__":
    # Consultar por un número específico (ej: 573001234567)
    numero = input("Ingrese el número celular a consultar (solo dígitos): ").strip()
    
    if numero.isdigit():
        resultado = consultar_por_celular(numero)
        
        # Mostrar preview si hay resultados
        if resultado is not None and not resultado.empty:
            print("\n🔍 Vista previa de los datos:")
            print(resultado.head(3))
    else:
        print("❌ El número debe contener solo dígitos")