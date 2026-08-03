import pandas as pd
import pdfplumber
import re
import json

MONTO_BUSCAR = 22.00

print("="*80)
print(f"🔍 ANÁLISIS COMPLETO DE VENTAS Y COBROS DE S/ {MONTO_BUSCAR}")
print("="*80)

# ============================================================
# 1. VENTAS EN CAJA DEL 30/07
# ============================================================
print("\n📄 [1] TODAS LAS VENTAS DE S/ 22 EN LOS PDFs")
print("-"*80)

def parsear_ref(texto):
    if not texto: return None, []
    texto_lower = texto.replace("\n", " ").lower()
    origen = None
    m_o = re.search(r"\b(izi?|bcp|yape|plin|bim)\b", texto_lower)
    if m_o:
        val = m_o.group(1).upper()
        if val == "IZ": val = "IZI"
        origen = val
    texto_sin_horas = re.sub(r"\b\d{1,2}:\d{2}\b", "", texto)
    nums = re.findall(r"\b(\d{5,})\b", texto_sin_horas)
    return origen, nums

for pdf_name in ["caja1.pdf", "caja2.pdf"]:
    print(f"\n📄 {pdf_name}:")
    try:
        with pdfplumber.open(pdf_name) as pdf:
            for page in pdf.pages:
                for tabla in page.extract_tables():
                    for fila in tabla:
                        if fila and len(fila) >= 12 and fila[1] == "Venta":
                            try:
                                monto = float(fila[10].replace(",", "")) if fila[10] else 0
                                if abs(monto - MONTO_BUSCAR) <= 0.10:
                                    metodo_raw = (fila[2] or "").replace("\n", " ")
                                    origen, nums = parsear_ref(fila[2] or "")
                                    print(f"   Op #{fila[0]:<5} | {metodo_raw[:30]:<30} | S/ {monto} | Origen: {origen} | Nums: {nums}")
                            except: pass
    except Exception as e:
        print(f"   ❌ Error: {e}")

# ============================================================
# 2. IZIPAY DEL 30/07 CON MONTO 22
# ============================================================
print("\n\n💳 [2] COBROS IZIPAY CON MONTO S/ 22")
print("-"*80)

try:
    df_izi = pd.read_excel("izipay.xlsx")
    df_izi["Fecha y hora"] = pd.to_datetime(df_izi["Fecha y hora"], dayfirst=True)
    df_izi["Monto total"] = pd.to_numeric(df_izi["Monto total"], errors='coerce')
    
    # Filtrar por monto (con tolerancia)
    df_22 = df_izi[abs(df_izi["Monto total"] - MONTO_BUSCAR) <= 0.10].copy()
    df_22["Hora"] = df_22["Fecha y hora"].dt.strftime("%d/%m %H:%M")
    
    print(f"Total: {len(df_22)}")
    if len(df_22) > 0:
        for idx, row in df_22.iterrows():
            print(f"   {row['Hora']} | S/ {row['Monto total']} | {row['Medio de cobro']} | {row['Estado de venta']}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================
# 3. YAPE DEL 30/07 CON MONTO 22
# ============================================================
print("\n\n📲 [3] COBROS YAPE CON MONTO S/ 22")
print("-"*80)

try:
    df_temp = pd.read_excel("yape.xlsx", header=None)
    header_row = None
    for i, row in df_temp.iterrows():
        valores = [str(v).lower() for v in row.values if pd.notna(v)]
        if any("tipo" in v and "transac" in v for v in valores):
            header_row = i
            break
    
    if header_row is not None:
        df_yape = pd.read_excel("yape.xlsx", header=header_row)
        col_fecha = col_monto = None
        for c in df_yape.columns:
            cl = str(c).lower().strip()
            if "fecha" in cl and col_fecha is None: col_fecha = c
            if "monto" in cl and col_monto is None: col_monto = c
        
        df_yape[col_fecha] = pd.to_datetime(df_yape[col_fecha], dayfirst=True, errors='coerce')
        df_yape[col_monto] = pd.to_numeric(df_yape[col_monto], errors='coerce')
        
        df_y22 = df_yape[abs(df_yape[col_monto] - MONTO_BUSCAR) <= 0.10].copy()
        df_y22["Hora"] = df_y22[col_fecha].dt.strftime("%d/%m %H:%M")
        
        print(f"Total: {len(df_y22)}")
        if len(df_y22) > 0:
            for idx, row in df_y22.iterrows():
                print(f"   {row['Hora']} | S/ {row[col_monto]}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================
# 4. BCP DEL 30/07 CON MONTO 22
# ============================================================
print("\n\n🏦 [4] COBROS BCP CON MONTO S/ 22")
print("-"*80)

try:
    df_bcp = pd.read_excel("bcp.xlsx")
    col_fecha = col_monto = col_numop = col_desc = None
    for c in df_bcp.columns:
        cl = str(c).lower().strip()
        if "fecha" in cl and col_fecha is None: col_fecha = c
        if "monto" in cl and col_monto is None: col_monto = c
        if ("numero" in cl or "operac" in cl) and col_numop is None: col_numop = c
        if "descrip" in cl and col_desc is None: col_desc = c
    
    df_bcp[col_fecha] = pd.to_datetime(df_bcp[col_fecha], dayfirst=True, errors='coerce')
    df_bcp[col_monto] = pd.to_numeric(df_bcp[col_monto], errors='coerce')
    
    df_b22 = df_bcp[abs(df_bcp[col_monto] - MONTO_BUSCAR) <= 0.10].copy()
    df_b22["Fecha"] = df_b22[col_fecha].dt.strftime("%d/%m")
    
    print(f"Total: {len(df_b22)}")
    if len(df_b22) > 0:
        for idx, row in df_b22.iterrows():
            print(f"   {row['Fecha']} | S/ {row[col_monto]} | Op {row[col_numop]} | {row[col_desc][:30]}")
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================
# 5. RESUMEN
# ============================================================
print("\n\n" + "="*80)
print("💡 RESUMEN")
print("="*80)
print("Con esto podemos ver:")
print("- Cuántas ventas de S/22 hay en las cajas")
print("- Cuántos cobros de S/22 hay en cada canal")
print("- Si el número de operación del POS coincide con algún canal")
print("- Por qué la conciliación falla o no")