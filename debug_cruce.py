import pandas as pd
import pdfplumber
import re
import json

print("="*80)
print("🔍 DEBUG DE CRUCE - VAMOS A VER QUE PASA")
print("="*80)

# ============================================================
# 1. LEER BCP CRUDO
# ============================================================
print("\n📊 [1] LEYENDO BCP.xlsx TAL CUAL")
print("-"*80)
df_bcp = pd.read_excel("bcp.xlsx")
print(f"Columnas: {list(df_bcp.columns)}")
print(f"\nTIPOS DE DATOS:")
print(df_bcp.dtypes)
print(f"\nPRIMERAS 10 FILAS:")
print(df_bcp.head(10).to_string())

# Detectar columnas
col_numop = None
col_monto = None
for c in df_bcp.columns:
    cl = str(c).lower().strip()
    if "monto" in cl and col_monto is None: col_monto = c
    if ("numero" in cl or "operac" in cl) and col_numop is None: col_numop = c

print(f"\n📌 Columna número operación detectada: '{col_numop}'")
print(f"📌 Columna monto detectada: '{col_monto}'")

# Ver números TAL COMO ESTÁN
print(f"\n🔢 NÚMEROS DE OPERACIÓN BCP (tipos):")
for idx, val in enumerate(df_bcp[col_numop].head(15)):
    print(f"   Fila {idx}: valor='{val}' | tipo={type(val).__name__} | como_str='{str(val)}'")

# ============================================================
# 2. LEER PDFs Y EXTRAER REFERENCIAS
# ============================================================
print("\n\n📄 [2] LEYENDO PDFs Y BUSCANDO REFERENCIAS BCP")
print("-"*80)

def parsear_ref(texto_crudo):
    if not texto_crudo: return None
    texto = texto_crudo.replace("\n", " ").strip().lower()
    m_num = re.search(r"(?:izi?|bcp|yape|plin|bim)[\s/]+(\d{4,})", texto)
    if m_num:
        return m_num.group(1)
    return None

refs_pos = []
for pdf_name in ["caja1.pdf", "caja2.pdf"]:
    try:
        with pdfplumber.open(pdf_name) as pdf:
            for page in pdf.pages:
                for tabla in page.extract_tables():
                    for fila in tabla:
                        if fila and len(fila) >= 12 and fila[1] == "Venta":
                            metodo_raw = (fila[2] or "").replace("\n", " ")
                            num_ref = parsear_ref(fila[2] or "")
                            if num_ref and "bcp" in metodo_raw.lower():
                                monto = float(fila[10].replace(",", "")) if fila[10] else 0
                                refs_pos.append({
                                    "pdf": pdf_name,
                                    "op_pos": fila[0],
                                    "ref_completa": metodo_raw,
                                    "num_extraido": num_ref,
                                    "monto": monto
                                })
    except Exception as e:
        print(f"❌ Error leyendo {pdf_name}: {e}")

print(f"\n🎯 Referencias con 'bcp' en POS: {len(refs_pos)}")
print("\nDETALLE:")
for r in refs_pos:
    print(f"   [{r['pdf']} Op#{r['op_pos']}] Ref='{r['ref_completa']}' → num='{r['num_extraido']}' | S/ {r['monto']}")

# ============================================================
# 3. COMPARAR MANUALMENTE
# ============================================================
print("\n\n🔍 [3] INTENTANDO CRUZAR CADA REF DEL POS CON BCP")
print("-"*80)

for r in refs_pos:
    num_pos = r["num_extraido"]
    monto_pos = r["monto"]
    print(f"\n🎯 Buscando POS: num='{num_pos}' | monto=S/ {monto_pos}")
    
    encontrados = []
    for idx, row in df_bcp.iterrows():
        num_bcp_raw = row[col_numop]
        num_bcp_str = str(num_bcp_raw).strip()
        # Quitar .0 si es float
        if num_bcp_str.endswith(".0"):
            num_bcp_str = num_bcp_str[:-2]
        
        # Comparar sin ceros iniciales
        pos_limpio = num_pos.lstrip("0")
        bcp_limpio = num_bcp_str.lstrip("0")
        
        if pos_limpio == bcp_limpio:
            monto_bcp = row[col_monto]
            match_monto = abs(monto_bcp - monto_pos) <= 0.10
            estado = "✅ MATCH COMPLETO" if match_monto else "⚠️ NUM OK pero MONTO NO"
            encontrados.append(f"      {estado} → BCP fila {idx}: num='{num_bcp_str}' monto=S/ {monto_bcp}")
    
    if encontrados:
        for e in encontrados:
            print(e)
    else:
        print(f"      ❌ NO SE ENCONTRÓ EN BCP")
        # Buscar montos iguales al menos
        for idx, row in df_bcp.iterrows():
            if abs(row[col_monto] - monto_pos) <= 0.10:
                print(f"         💡 Pero HAY un BCP con mismo monto (fila {idx}): num='{row[col_numop]}' S/ {row[col_monto]}")

print("\n" + "="*80)
print("✅ DEBUG COMPLETO - Mándame TODO el output")
print("="*80)