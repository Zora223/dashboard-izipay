import pandas as pd
import json

print("="*80)
print("🔍 ANALIZANDO CRUCE DE S/ 22.00")
print("="*80)

# Leer izipay
df = pd.read_excel("izipay.xlsx")
df["Fecha y hora"] = pd.to_datetime(df["Fecha y hora"], dayfirst=True)

# TODAS las transacciones de S/ 22 en Izipay
print(f"\n📊 TODAS las transacciones Izipay con monto S/ 22.00:")
df_22 = df[df["Monto total"] == 22.00].copy()
df_22["Hora"] = df_22["Fecha y hora"].dt.strftime("%H:%M")
print(f"Total: {len(df_22)}")
if len(df_22) > 0:
    print(df_22[["Fecha y hora", "Hora", "Medio de cobro", "Monto total"]].to_string())

# Leer historial para ver ventas del POS con monto 22
print(f"\n\n📄 TODAS las ventas Yape/Tarjeta del POS con monto S/ 22.00:")
with open("historial.json", "r", encoding="utf-8") as f:
    data = json.load(f)

ventas = data.get("ventas", [])
ventas_22 = [v for v in ventas if v.get("monto_pagado") == 22.00 
             and v.get("metodo_pago") in ["Yape", "Tarjeta de crédito", "Tarjeta de débito"]]

print(f"Total: {len(ventas_22)}")
for v in ventas_22:
    print(f"   {v['fecha']} | {v['caja']} | Op#{v['n_op']} | {v['metodo_pago']} | Ref: '{v.get('raw_metodo', '')}'")

# Análisis
print(f"\n\n💡 ANÁLISIS:")
print("-"*80)
print(f"Cobros Izipay S/22: {len(df_22)}")
print(f"Ventas POS S/22:    {len(ventas_22)}")
if len(df_22) > 0 and len(ventas_22) > 0:
    if len(df_22) >= len(ventas_22):
        print(f"✅ Hay suficientes cobros Izipay para cubrir todas las ventas")
    else:
        print(f"⚠️ Hay MÁS ventas POS que cobros Izipay → algunas quedarán sin cruzar")