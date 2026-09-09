# ============================================================
# TALLER DE ANÁLISIS DE DATOS - MISIÓN 1
# Dataset: Supermarket Sales (1000 registros)
# Sector: Retail / Comercio Minorista
# ============================================================

import pandas as pd #librería principal para manipulación y análisis de datos estructurados. - Leer archivos (CSV, Excel, SQL, JSON, etc.) - 
#Limpiar datos (nulos, duplicados, transformaciones) - Filtrar, agrupar y agregar datos - Crear nuevas columnas
import numpy as np #es la base del cálculo numérico en Python. - Funciones estadísticas básicas - Operaciones matemáticas rápidas
import matplotlib.pyplot as plt #es la librería base para visualización de datos. - Gráficos de líneas - Barras - Histogramas - Dispersión
import seaborn as sns # librería de visualización basada en matplotlib pero más estadística y elegante por defecto.
# Gráficos más estéticos automáticamente - Visualizaciones estadísticas - Mapas de calor - Distribuciones
from scipy import stats #es un módulo para estadística avanzada. - Estadística inferencial

# ─────────────────────────────────────────────
# PASO 1 — CARGUE DEL DATASET (descarga directa)
# ─────────────────────────────────────────────
URL = (
    "https://raw.githubusercontent.com/sushantag9/"
    "Supermarket-Sales-Data-Analysis/master/"
    "supermarket_sales%20-%20Sheet1.csv"
)

print("⏳ Descargando dataset...")
df = pd.read_csv(URL)
print(f"✅ Dataset cargado: {df.shape[0]} filas × {df.shape[1]} columnas\n")

# ─────────────────────────────────────────────
# PASO 2 — VISUALIZAR PRIMEROS / ÚLTIMOS REGISTROS
# ─────────────────────────────────────────────
print("═" * 55)
print("PRIMEROS 5 REGISTROS (head)")
print("═" * 55)
print(df.head())

print("\n" + "═" * 55)
print("ÚLTIMOS 5 REGISTROS (tail)")
print("═" * 55)
print(df.tail())

# Resumen general
print("\n" + "═" * 55)
print("INFO GENERAL")
print("═" * 55)
print(df.info())

# ─────────────────────────────────────────────
# PASO 3 — SELECCIONAR COLUMNAS
# ─────────────────────────────────────────────
print("\n" + "═" * 55)
print("COLUMNAS SELECCIONADAS: Branch, Product line, Total, Rating")
print("═" * 55)
cols = df[["Branch", "Product line", "Total", "Rating"]]
print(cols.head(10))

# ─────────────────────────────────────────────
# PASO 4 — FILTRAR FILAS
# ─────────────────────────────────────────────
print("\n" + "═" * 55)
print("FILTRO: Ventas con Total > 300 USD")
print("═" * 55)
df_altas = df[df["Total"] > 300]
print(f"Registros encontrados: {len(df_altas)}")
print(df_altas[["Branch", "Product line", "Total"]].head())

# ─────────────────────────────────────────────
# PASO 5 — AGREGAR NUEVA COLUMNA
# ─────────────────────────────────────────────
df["Total_sin_impuesto"] = df["Total"] - df["Tax 5%"]
print("\n✅ Nueva columna 'Total_sin_impuesto' creada.")
print(df[["Total", "Tax 5%", "Total_sin_impuesto"]].head())

# ─────────────────────────────────────────────
# PASO 6 — ELIMINAR COLUMNAS INNECESARIAS
# ─────────────────────────────────────────────
df_clean = df.drop(columns=["gross margin percentage", "Invoice ID"])
print(f"\n✅ Columnas eliminadas. Quedan {df_clean.shape[1]} columnas.")

# ─────────────────────────────────────────────
# PASO 7 — AGRUPAR DATOS (GROUP BY)
# ─────────────────────────────────────────────
print("\n" + "═" * 55)
print("GROUP BY: Ventas totales por línea de producto")
print("═" * 55)
ventas_por_producto = (
    df.groupby("Product line")["Total"]
    .agg(["sum", "mean", "count"])
    .rename(columns={"sum": "Total_Ventas", "mean": "Promedio", "count": "Transacciones"})
    .sort_values("Total_Ventas", ascending=False)
)
print(ventas_por_producto.round(2))

print("\n" + "═" * 55)
print("GROUP BY: Rating promedio por sucursal")
print("═" * 55)
rating_sucursal = df.groupby("Branch")["Rating"].mean().round(2)
print(rating_sucursal)

# ─────────────────────────────────────────────
# PASO 8 — ORDENAR DATOS
# ─────────────────────────────────────────────
print("\n" + "═" * 55)
print("TOP 10 VENTAS (sort_values por Total, descendente)")
print("═" * 55)
df_sorted = df.sort_values("Total", ascending=False)
print(df_sorted[["Branch", "Product line", "Total", "Rating"]].head(10))

# ─────────────────────────────────────────────
# PASO 9 — ESTADÍSTICAS DE TENDENCIA CENTRAL
# ─────────────────────────────────────────────
col_analisis = "Total"
print("\n" + "═" * 55)
print(f"ESTADÍSTICAS DE TENDENCIA CENTRAL — columna: '{col_analisis}'")
print("═" * 55)
media    = df[col_analisis].mean()
mediana  = df[col_analisis].median()
moda     = df[col_analisis].mode()[0]
print(f"  📊 Media   : {media:.2f}")
print(f"  📊 Mediana : {mediana:.2f}")
print(f"  📊 Moda    : {moda:.2f}")

# ─────────────────────────────────────────────
# PASO 10 — ESTADÍSTICAS DE DISPERSIÓN
# ─────────────────────────────────────────────
print("\n" + "═" * 55)
print(f"ESTADÍSTICAS DE DISPERSIÓN — columna: '{col_analisis}'")
print("═" * 55)
varianza = df[col_analisis].var()
desv_std = df[col_analisis].std()
moda_dis = df[col_analisis].mode()[0]
print(f"  📉 Varianza          : {varianza:.2f}")
print(f"  📉 Desviación Estándar: {desv_std:.2f}")
print(f"  📉 Moda              : {moda_dis:.2f}")

# ─────────────────────────────────────────────
# PASO 11 — GRÁFICAS
# ─────────────────────────────────────────────
fig_size = (9, 5)
colores  = sns.color_palette("Set2")

# ── 1. Gráfico de BARRAS — Ventas por línea de producto
plt.figure(figsize=fig_size)
ventas_por_producto["Total_Ventas"].sort_values().plot(
    kind="barh", color=colores, edgecolor="white"
)
plt.title("Ventas Totales por Línea de Producto", fontsize=14, fontweight="bold")
plt.xlabel("Total Ventas (USD)")
plt.tight_layout()
plt.savefig("grafica_barras.png", dpi=150)
plt.show()
print("✅ Guardada: grafica_barras.png")

# ── 2. Gráfico de LÍNEAS — Ventas en el tiempo
df["Date"] = pd.to_datetime(df["Date"])
ventas_dia = df.groupby("Date")["Total"].sum().sort_index()

plt.figure(figsize=fig_size)
ventas_dia.plot(kind="line", color="#2196F3", linewidth=2)
plt.title("Ventas Diarias en el Tiempo", fontsize=14, fontweight="bold")
plt.xlabel("Fecha")
plt.ylabel("Total Ventas (USD)")
plt.tight_layout()
plt.savefig("grafica_lineas.png", dpi=150)
plt.show()
print("✅ Guardada: grafica_lineas.png")

# ── 3. Gráfico de PASTEL — Participación por método de pago
pago = df["Payment"].value_counts()

plt.figure(figsize=(7, 7))
plt.pie(
    pago, labels=pago.index, autopct="%1.1f%%",
    colors=colores, startangle=90, wedgeprops={"edgecolor": "white"}
)
plt.title("Distribución por Método de Pago", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("grafica_pastel.png", dpi=150)
plt.show()
print("✅ Guardada: grafica_pastel.png")

# ── 4. HISTOGRAMA — Distribución del Total de ventas
plt.figure(figsize=fig_size)
plt.hist(df["Total"], bins=30, color="#4CAF50", edgecolor="white", alpha=0.85)
plt.axvline(media,   color="red",    linestyle="--", linewidth=1.5, label=f"Media: {media:.0f}")
plt.axvline(mediana, color="orange", linestyle="--", linewidth=1.5, label=f"Mediana: {mediana:.0f}")
plt.title("Distribución del Total de Ventas", fontsize=14, fontweight="bold")
plt.xlabel("Total (USD)")
plt.ylabel("Frecuencia")
plt.legend()
plt.tight_layout()
plt.savefig("grafica_histograma.png", dpi=150)
plt.show()
print("✅ Guardada: grafica_histograma.png")

# ── 5. MAPA DE CALOR — Correlación entre variables numéricas
plt.figure(figsize=(9, 6))
num_cols = df.select_dtypes(include=np.number).drop(columns=["Total_sin_impuesto"])
corr     = num_cols.corr()
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="coolwarm",
    linewidths=0.5, linecolor="white", square=True
)
plt.title("Mapa de Calor — Correlación de Variables", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("grafica_heatmap.png", dpi=150)
plt.show()
print("✅ Guardada: grafica_heatmap.png")

print("\n🎯 ¡Taller completado exitosamente!")
