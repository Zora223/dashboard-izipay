import pdfplumber
import pandas as pd

print("="*60)
print("📊 LECTURA DE ARCHIVOS - DASHBOARD IZIPAY")
print("="*60)

# ============================
# 1. LEER EL EXCEL DE IZIPAY
# ============================
print("\n📥 Leyendo Izipay...")
df_izipay = pd.read_excel("izipay.xlsx")
print("✅ Izipay cargado correctamente")
print(f"📌 Total transacciones: {len(df_izipay)}")
print(f"📌 Columnas: {list(df_izipay.columns)}")
print("\n🔍 Primeras 5 filas:")
print(df_izipay.head())

# ============================
# 2. LEER PDF CAJA 1
# ============================
print("\n" + "="*60)
print("📥 Leyendo REPORTE CAJA 1...")
filas_caja1 = []
with pdfplumber.open("caja1.pdf") as pdf:
    print(f"📄 Total páginas: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        tablas = page.extract_tables()
        for tabla in tablas:
            for fila in tabla:
                filas_caja1.append(fila)

print(f"✅ Caja 1 - {len(filas_caja1)} filas extraídas")
print("\n🔍 Primeras 5 filas de Caja 1:")
for f in filas_caja1[:5]:
    print(f)

# ============================
# 3. LEER PDF CAJA 2
# ============================
print("\n" + "="*60)
print("📥 Leyendo REPORTE CAJA 2...")
filas_caja2 = []
with pdfplumber.open("caja2.pdf") as pdf:
    print(f"📄 Total páginas: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        tablas = page.extract_tables()
        for tabla in tablas:
            for fila in tabla:
                filas_caja2.append(fila)

print(f"✅ Caja 2 - {len(filas_caja2)} filas extraídas")
print("\n🔍 Primeras 5 filas de Caja 2:")
for f in filas_caja2[:5]:
    print(f)

print("\n" + "="*60)
print("✅ LECTURA COMPLETADA")
print("="*60)