import json
import pandas as pd

print("="*80)
print("🔍 DEBUG - REVISANDO HISTORIAL.JSON")
print("="*80)

with open("historial.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ============================================================
# 1. VER BCP GUARDADO
# ============================================================
print(f"\n📊 BCP GUARDADO EN HISTORIAL: {len(data.get('bcp', []))} registros")
print("-"*80)
bcp = data.get("bcp", [])
if bcp:
    print(f"\n{'Fecha':<15}{'Monto':<12}{'Num Op':<15}{'es_venta':<10}{'Descripción'}")
    print("-"*80)
    for b in bcp[:20]:
        fecha = b['fecha_hora'][:10]
        monto = b['monto']
        num = b.get('num_operacion', '')
        es_v = b.get('es_venta', True)
        desc = b.get('descripcion', '')[:30]
        print(f"{fecha:<15}{monto:<12}{num:<15}{str(es_v):<10}{desc}")

# ============================================================
# 2. VER VENTAS DIGITALES DEL POS
# ============================================================
print(f"\n\n📄 VENTAS DIGITALES DEL POS")
print("-"*80)
ventas = data.get("ventas", [])
digitales = [v for v in ventas if v.get("metodo_pago") in ["Yape", "Tarjeta de crédito", "Tarjeta de débito"]]
print(f"Total digitales: {len(digitales)}")

# Solo las que tienen referencia con número
print(f"\n{'Caja':<8}{'Op':<6}{'Método':<20}{'Num Op':<15}{'Monto':<10}{'Ref completa'}")
print("-"*100)
for v in digitales[:30]:
    num = v.get('num_operacion') or ''
    ref = v.get('raw_metodo', '')[:40]
    print(f"{v['caja']:<8}{str(v['n_op']):<6}{v['metodo_pago']:<20}{num:<15}{v['monto_pagado']:<10}{ref}")

# ============================================================
# 3. INTENTAR CRUCE MANUAL POR MONTO
# ============================================================
print(f"\n\n🔍 CRUCE MANUAL: ALERTAS vs BCP HUERFANOS")
print("-"*80)

# Simular cruce
montos_bcp = [(b['monto'], b.get('num_operacion', ''), b.get('descripcion', '')[:30]) for b in bcp if b.get('es_venta', True)]

# Buscar cada venta digital en BCP
matches = 0
sin_match = 0
for v in digitales:
    monto_pos = v['monto_pagado']
    encontrado = False
    for m_bcp, n_bcp, d_bcp in montos_bcp:
        if abs(m_bcp - monto_pos) <= 0.10:
            encontrado = True
            print(f"✅ MATCH: POS S/{monto_pos} (Op#{v['n_op']}) ↔ BCP S/{m_bcp} (Op {n_bcp}) - {d_bcp}")
            matches += 1
            break
    if not encontrado and v.get('metodo_pago') == "Yape":
        sin_match += 1

print(f"\n📊 RESUMEN:")
print(f"   Total ventas digitales: {len(digitales)}")
print(f"   Con match potencial en BCP (por monto): {matches}")
print(f"   Yape sin match: {sin_match}")

# ============================================================
# 4. BCP QUE PODRIA ESTAR CRUZANDO
# ============================================================
print(f"\n\n🏦 TODOS LOS BCP CON es_venta=True:")
print("-"*80)
bcp_ventas = [b for b in bcp if b.get('es_venta', True)]
print(f"Total: {len(bcp_ventas)}")
for b in bcp_ventas:
    print(f"   S/ {b['monto']:<10} | Op {b.get('num_operacion', ''):<12} | {b.get('descripcion', '')[:40]}")

print("\n" + "="*80)