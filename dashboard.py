import pdfplumber
import pandas as pd
import re
from datetime import datetime

print("="*70)
print("📊 DASHBOARD GERENCIAL - CONTROL ANTI-FRAUDE")
print("="*70)

# ============================================================
# FUNCIÓN: Extraer resumen de una caja
# ============================================================
def extraer_resumen_caja(pdf_path, nombre_caja):
    resumen = {"caja": nombre_caja}
    ventas = []
    metodos_pago = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        # Extraer texto de la primera página para info general
        texto = pdf.pages[0].extract_text()
        
        # Extraer datos con regex
        vendedor = re.search(r"Vendedor:\s*(.+?)\s+Fecha", texto)
        apertura = re.search(r"apertura:\s*(.+?)\n", texto)
        cierre = re.search(r"cierre:\s*(.+?)\n", texto)
        ingreso = re.search(r"Ingreso caja:\s*S/\.\s*([\d,.]+)", texto)
        total_efectivo = re.search(r"Total efectivo:\s*S/\s*([\d,.]+)", texto)
        
        resumen["vendedor"] = vendedor.group(1) if vendedor else "N/A"
        resumen["apertura"] = apertura.group(1) if apertura else "N/A"
        resumen["cierre"] = cierre.group(1) if cierre else "N/A"
        resumen["ingreso_total"] = float(ingreso.group(1).replace(",", "")) if ingreso else 0
        resumen["total_efectivo"] = float(total_efectivo.group(1).replace(",", "")) if total_efectivo else 0
        
        # Extraer tabla de métodos de pago y ventas
        for page in pdf.pages:
            tablas = page.extract_tables()
            for tabla in tablas:
                for fila in tabla:
                    if fila and len(fila) >= 3:
                        # Métodos de pago (Efectivo, Yape, Tarjeta)
                        if fila[1] in ["Efectivo", "Yape", "Tarjeta de crédito", "Tarjeta de débito"]:
                            try:
                                metodos_pago[fila[1]] = float(fila[2].replace(",", ""))
                            except:
                                pass
                        
                        # Ventas individuales
                        if len(fila) >= 11 and fila[1] == "Venta":
                            try:
                                ventas.append({
                                    "caja": nombre_caja,
                                    "tipo": fila[1],
                                    "metodo_pago": fila[2],
                                    "fecha": fila[5],
                                    "total": float(fila[10].replace(",", ""))
                                })
                            except:
                                pass
    
    resumen["metodos_pago"] = metodos_pago
    return resumen, ventas

# ============================================================
# 1. EXTRAER DATOS DE LAS CAJAS
# ============================================================
print("\n📥 Procesando Caja 1...")
resumen_c1, ventas_c1 = extraer_resumen_caja("caja1.pdf", "Caja 1")

print("📥 Procesando Caja 2...")
resumen_c2, ventas_c2 = extraer_resumen_caja("caja2.pdf", "Caja 2")

# ============================================================
# 2. LEER IZIPAY
# ============================================================
print("📥 Procesando Izipay...")
df_izipay = pd.read_excel("izipay.xlsx")
df_izipay["Fecha y hora"] = pd.to_datetime(df_izipay["Fecha y hora"])
df_izipay["Hora"] = df_izipay["Fecha y hora"].dt.hour

# ============================================================
# 3. MOSTRAR RESUMEN
# ============================================================
print("\n" + "="*70)
print("📋 RESUMEN POR CAJA")
print("="*70)

for r in [resumen_c1, resumen_c2]:
    print(f"\n🏪 {r['caja']} - {r['vendedor']}")
    print(f"   ⏰ {r['apertura']} → {r['cierre']}")
    print(f"   💰 Ingreso total: S/ {r['ingreso_total']:.2f}")
    print(f"   💵 Efectivo: S/ {r['total_efectivo']:.2f}")
    print(f"   📊 Métodos de pago:")
    for metodo, monto in r["metodos_pago"].items():
        print(f"      • {metodo}: S/ {monto:.2f}")

# ============================================================
# 4. CONCILIACIÓN CON IZIPAY
# ============================================================
print("\n" + "="*70)
print("🔍 CONCILIACIÓN CAJA vs IZIPAY")
print("="*70)

# Total digital según cajas (Yape + Tarjetas)
total_digital_cajas = 0
for r in [resumen_c1, resumen_c2]:
    for metodo, monto in r["metodos_pago"].items():
        if metodo != "Efectivo":
            total_digital_cajas += monto

total_izipay = df_izipay["Monto total"].sum()
diferencia = total_digital_cajas - total_izipay

print(f"\n💳 Total DIGITAL registrado en Cajas: S/ {total_digital_cajas:.2f}")
print(f"💳 Total cobrado en IZIPAY:           S/ {total_izipay:.2f}")
print(f"⚠️  DIFERENCIA:                        S/ {diferencia:.2f}")

if abs(diferencia) < 1:
    print("\n✅ TODO CUADRA - Sin alertas")
elif diferencia > 0:
    print(f"\n🚨 ALERTA: Las cajas registraron S/ {diferencia:.2f} MÁS que Izipay")
    print("   → Posible venta registrada que NO se cobró realmente")
else:
    print(f"\n🚨 ALERTA: Izipay cobró S/ {abs(diferencia):.2f} MÁS que las cajas")
    print("   → Posible cobro NO registrado (posible fraude)")

# Guardar Izipay procesado
df_izipay.to_excel("izipay_procesado.xlsx", index=False)

print("\n" + "="*70)
print("✅ PROCESO COMPLETADO")
print("="*70)