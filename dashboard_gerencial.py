import pdfplumber
import pandas as pd
import re
import plotly.graph_objects as go
from datetime import datetime

print("🎨 Generando Dashboard Gerencial Premium v3...")

# ============================================================
# FUNCIONES DE EXTRACCIÓN
# ============================================================
def parsear_metodo_pago(texto_crudo):
    if not texto_crudo: return ("Desconocido", None, None)
    texto = texto_crudo.replace("\n", " ").strip()
    metodo = "Otro"
    if "Yape" in texto: metodo = "Yape"
    elif "Tarjeta de\ncrédito" in texto_crudo or "Tarjeta de crédito" in texto: metodo = "Tarjeta de crédito"
    elif "Tarjeta de\ndébito" in texto_crudo or "Tarjeta de débito" in texto: metodo = "Tarjeta de débito"
    elif "Efectivo" in texto: metodo = "Efectivo"
    origen = None
    m_o = re.search(r"(izi|bcp|yape|plin)", texto.lower())
    if m_o: origen = m_o.group(1).upper()
    hora_ref = None
    m_h = re.search(r"(\d{1,2}):(\d{2})", texto)
    if m_h:
        h, m = int(m_h.group(1)), int(m_h.group(2))
        if 0 <= h < 24 and 0 <= m < 60:
            hora_ref = f"{h:02d}:{m:02d}"
    return (metodo, hora_ref, origen)

def extraer_ventas(pdf_path, nombre_caja):
    ventas = []
    resumen = {}
    with pdfplumber.open(pdf_path) as pdf:
        texto = pdf.pages[0].extract_text()
        vendedor = re.search(r"Vendedor:\s*(.+?)\s+Fecha", texto)
        ingreso = re.search(r"Ingreso caja:\s*S/\.\s*([\d,.]+)", texto)
        efectivo = re.search(r"Total efectivo:\s*S/\s*([\d,.]+)", texto)
        saldo_inicial = re.search(r"Saldo inicial:\s*S/\.\s*([\d,.]+)", texto)
        saldo_final = re.search(r"Saldo final:\s*S/\.\s*([\d,.]+)", texto)
        apertura = re.search(r"apertura:\s*(.+?)\n", texto)
        cierre = re.search(r"cierre:\s*(.+?)\n", texto)
        
        resumen["caja"] = nombre_caja
        resumen["vendedor"] = vendedor.group(1) if vendedor else "N/A"
        resumen["apertura"] = apertura.group(1) if apertura else ""
        resumen["cierre"] = cierre.group(1) if cierre else ""
        resumen["ingreso_total"] = float(ingreso.group(1).replace(",", "")) if ingreso else 0
        resumen["total_efectivo"] = float(efectivo.group(1).replace(",", "")) if efectivo else 0
        resumen["saldo_inicial"] = float(saldo_inicial.group(1).replace(",", "")) if saldo_inicial else 0
        resumen["saldo_final"] = float(saldo_final.group(1).replace(",", "")) if saldo_final else 0
        
        for page in pdf.pages:
            for tabla in page.extract_tables():
                for fila in tabla:
                    if fila and len(fila) >= 12 and fila[1] == "Venta":
                        try:
                            metodo, hora_ref, origen = parsear_metodo_pago(fila[2] or "")
                            ventas.append({
                                "caja": nombre_caja,
                                "vendedor": resumen["vendedor"],
                                "n_op": fila[0],
                                "metodo_pago": metodo,
                                "hora_referencia": hora_ref,
                                "origen_ref": origen,
                                "documento": fila[4],
                                "monto_pagado": float(fila[10].replace(",", "")) if fila[10] else 0,
                            })
                        except: pass
    return resumen, ventas

# ============================================================
# CARGAR DATOS
# ============================================================
r1, v1 = extraer_ventas("caja1.pdf", "Caja 1")
r2, v2 = extraer_ventas("caja2.pdf", "Caja 2")
df_ventas = pd.DataFrame(v1 + v2)
df_digital = df_ventas[df_ventas["metodo_pago"].isin(["Yape", "Tarjeta de crédito", "Tarjeta de débito"])].copy()

df_izipay = pd.read_excel("izipay.xlsx")
df_izipay["Fecha y hora"] = pd.to_datetime(df_izipay["Fecha y hora"], dayfirst=True)
df_izipay["Hora_str"] = df_izipay["Fecha y hora"].dt.strftime("%H:%M")
df_izipay["Hora"] = df_izipay["Fecha y hora"].dt.hour
df_izipay["Hora_minutos"] = df_izipay["Fecha y hora"].dt.hour * 60 + df_izipay["Fecha y hora"].dt.minute
df_izipay["Usado"] = False
df_izipay["Monto total"] = df_izipay["Monto total"].astype(float)

def h2m(h):
    if not isinstance(h, str): return None
    try:
        a, b = map(int, h.split(":"))
        return a * 60 + b
    except: return None

# CONCILIAR
resultados = []
for _, v in df_digital.iterrows():
    hm = h2m(v["hora_referencia"])
    match, diff = None, 999
    for i, iz in df_izipay[~df_izipay["Usado"]].iterrows():
        if abs(iz["Monto total"] - v["monto_pagado"]) <= 0.10:
            if hm is not None:
                d = abs(iz["Hora_minutos"] - hm)
                if d <= 10 and d < diff:
                    match, diff = i, d
            elif match is None:
                match, diff = i, -1
    estado = "🚨 SIN COBRO"
    izi_h, izi_m, izi_med = "-", "-", "-"
    if match is not None:
        df_izipay.at[match, "Usado"] = True
        estado = "✅ OK" if diff <= 2 else f"⚠️ ±{diff}min"
        izi_h = df_izipay.loc[match, "Hora_str"]
        izi_m = f"S/ {df_izipay.loc[match, 'Monto total']:.2f}"
        izi_med = df_izipay.loc[match, "Medio de cobro"]
    resultados.append({
        "Caja": v["caja"], "Op": v["n_op"], "Doc": v["documento"],
        "Método": v["metodo_pago"], "Hora Ref": v["hora_referencia"] or "-",
        "Monto": v["monto_pagado"], "Estado": estado,
        "Izipay Hora": izi_h, "Izipay Monto": izi_m, "Izipay Medio": izi_med
    })

df_res = pd.DataFrame(resultados)
alertas_caja = df_res[df_res["Estado"].str.contains("SIN COBRO")]
izipay_huerf = df_izipay[~df_izipay["Usado"]].copy()

# ============================================================
# CÁLCULO DE QUIEBRES POR CAJA
# ============================================================
def calcular_quiebre_caja(resumen, ventas, alertas_df, huerfanos_df, nombre):
    """Calcula el cuadre teórico vs real por caja"""
    ventas_caja = [v for v in ventas if v["caja"] == nombre]
    df_v = pd.DataFrame(ventas_caja)
    
    if len(df_v) == 0:
        return None
    
    efectivo_ventas = df_v[df_v["metodo_pago"] == "Efectivo"]["monto_pagado"].sum()
    yape_ventas = df_v[df_v["metodo_pago"] == "Yape"]["monto_pagado"].sum()
    tarjeta_ventas = df_v[df_v["metodo_pago"].str.contains("Tarjeta")]["monto_pagado"].sum()
    total_ventas = efectivo_ventas + yape_ventas + tarjeta_ventas
    
    # Alertas de esta caja
    alertas_c = alertas_df[alertas_df["Caja"] == nombre]
    monto_alertas = alertas_c["Monto"].sum()
    
    # Diferencia esperada (saldo final vs saldo inicial + ventas)
    diferencia_caja = resumen["saldo_final"] - (resumen["saldo_inicial"] + efectivo_ventas)
    
    return {
        "caja": nombre,
        "vendedor": resumen["vendedor"],
        "apertura": resumen["apertura"],
        "cierre": resumen["cierre"],
        "saldo_inicial": resumen["saldo_inicial"],
        "saldo_final": resumen["saldo_final"],
        "efectivo_ventas": efectivo_ventas,
        "yape_ventas": yape_ventas,
        "tarjeta_ventas": tarjeta_ventas,
        "total_ventas": total_ventas,
        "total_transacciones": len(df_v),
        "alertas": len(alertas_c),
        "monto_alertas": monto_alertas,
        "diferencia_efectivo": diferencia_caja
    }

quiebre_c1 = calcular_quiebre_caja(r1, v1 + v2, alertas_caja, izipay_huerf, "Caja 1")
quiebre_c2 = calcular_quiebre_caja(r2, v1 + v2, alertas_caja, izipay_huerf, "Caja 2")

# TOTALES
efectivo_total = r1["total_efectivo"] + r2["total_efectivo"]
digital_total = df_digital["monto_pagado"].sum()
izipay_total = df_izipay["Monto total"].sum()
diferencia = digital_total - izipay_total
ingreso_total = r1["ingreso_total"] + r2["ingreso_total"]
monto_sospechoso = alertas_caja["Monto"].sum()
monto_no_reg = izipay_huerf["Monto total"].sum()
riesgo_total = monto_sospechoso + monto_no_reg

# ============================================================
# GRÁFICOS
# ============================================================
vh = df_izipay.groupby("Hora")["Monto total"].sum().reset_index()
fig_hora = go.Figure()
fig_hora.add_trace(go.Bar(
    x=vh["Hora"], y=vh["Monto total"],
    marker=dict(color=vh["Monto total"], colorscale=[[0, "#DBEAFE"], [1, "#1E40AF"]], showscale=False),
    text=[f"S/{v:.0f}" for v in vh["Monto total"]],
    textposition="outside", textfont=dict(size=11)
))
fig_hora.update_layout(
    title=dict(text="<b>📈 Flujo de Ventas por Hora - Izipay</b>", font=dict(size=16)),
    xaxis=dict(title="Hora", tickmode='linear', dtick=1),
    yaxis=dict(title="Monto (S/)", gridcolor="#E5E7EB"),
    plot_bgcolor="white", paper_bgcolor="white", height=380, margin=dict(t=60, b=50, l=50, r=30)
)

metodos = {
    "💵 Efectivo": efectivo_total,
    "📱 Yape/QR": df_digital[df_digital["metodo_pago"] == "Yape"]["monto_pagado"].sum(),
    "💳 T. Crédito": df_digital[df_digital["metodo_pago"] == "Tarjeta de crédito"]["monto_pagado"].sum(),
    "💳 T. Débito": df_digital[df_digital["metodo_pago"] == "Tarjeta de débito"]["monto_pagado"].sum(),
}
fig_metodo = go.Figure(data=[go.Pie(
    labels=list(metodos.keys()), values=list(metodos.values()),
    hole=0.55, marker=dict(colors=["#059669", "#7C3AED", "#D97706", "#0891B2"], line=dict(color="white", width=3)),
    textinfo="label+percent", textfont=dict(size=12, color="white")
)])
fig_metodo.update_layout(
    title=dict(text="<b>🥧 Distribución por Método</b>", font=dict(size=16)),
    showlegend=False, height=380, paper_bgcolor="white",
    annotations=[dict(text=f"<b>S/ {ingreso_total:,.0f}</b><br><span style='font-size:11px;color:gray'>Total Día</span>",
                     x=0.5, y=0.5, font=dict(size=18), showarrow=False)]
)

fig_cajas = go.Figure(data=[
    go.Bar(name='💵 Efectivo', x=["Caja 1", "Caja 2"], y=[r1["total_efectivo"], r2["total_efectivo"]],
           marker_color="#059669", text=[f"S/{r1['total_efectivo']:.0f}", f"S/{r2['total_efectivo']:.0f}"], textposition='outside'),
    go.Bar(name='📱 Digital', x=["Caja 1", "Caja 2"], 
           y=[r1["ingreso_total"] - r1["total_efectivo"], r2["ingreso_total"] - r2["total_efectivo"]],
           marker_color="#7C3AED", text=[f"S/{(r1['ingreso_total'] - r1['total_efectivo']):.0f}", 
                                          f"S/{(r2['ingreso_total'] - r2['total_efectivo']):.0f}"], textposition='outside')
])
fig_cajas.update_layout(
    title=dict(text="<b>🏪 Rendimiento por Caja</b>", font=dict(size=16)),
    barmode='group', plot_bgcolor="white", paper_bgcolor="white",
    height=380, yaxis=dict(gridcolor="#E5E7EB"), legend=dict(orientation="h", y=1.1),
    margin=dict(t=80, b=50, l=50, r=30)
)

izi_qr = df_izipay[df_izipay["Medio de cobro"] == "sQR"]["Monto total"].sum()
izi_tar = df_izipay[df_izipay["Medio de cobro"] != "sQR"]["Monto total"].sum()
caja_yape = df_digital[df_digital["metodo_pago"] == "Yape"]["monto_pagado"].sum()
caja_tar = df_digital[df_digital["metodo_pago"].str.contains("Tarjeta")]["monto_pagado"].sum()
fig_conc = go.Figure(data=[
    go.Bar(name='🏪 Caja', x=["Yape/QR", "Tarjetas"], y=[caja_yape, caja_tar],
           marker_color="#1E40AF", text=[f"S/{caja_yape:.2f}", f"S/{caja_tar:.2f}"], textposition='outside'),
    go.Bar(name='💳 Izipay', x=["Yape/QR", "Tarjetas"], y=[izi_qr, izi_tar],
           marker_color="#DC2626", text=[f"S/{izi_qr:.2f}", f"S/{izi_tar:.2f}"], textposition='outside')
])
fig_conc.update_layout(
    title=dict(text="<b>⚖️ Conciliación: Caja vs Izipay</b>", font=dict(size=16)),
    barmode='group', plot_bgcolor="white", paper_bgcolor="white",
    height=380, yaxis=dict(gridcolor="#E5E7EB"), legend=dict(orientation="h", y=1.1),
    margin=dict(t=80, b=50, l=50, r=30)
)

# ============================================================
# HTML - TARJETA DE QUIEBRE POR CAJA
# ============================================================
def tarjeta_quiebre_caja(q):
    if q is None:
        return ""
    
    # Estado de la caja
    if q["alertas"] == 0 and abs(q["diferencia_efectivo"]) < 1:
        estado_c = "SIN QUIEBRES"
        color_c = "#059669"
        icon_c = "✅"
        bg_c = "#ECFDF5"
    elif q["monto_alertas"] < 100:
        estado_c = "REVISAR"
        color_c = "#D97706"
        icon_c = "⚠️"
        bg_c = "#FEF3C7"
    else:
        estado_c = "CON QUIEBRES"
        color_c = "#DC2626"
        icon_c = "🚨"
        bg_c = "#FEE2E2"
    
    dif_color = "#059669" if abs(q["diferencia_efectivo"]) < 1 else "#DC2626"
    dif_signo = "+" if q["diferencia_efectivo"] > 0 else ""
    
    return f"""
    <div class="caja-card">
        <div class="caja-header" style="background: linear-gradient(135deg, {color_c}, {color_c}dd);">
            <div>
                <div class="caja-nombre">🏪 {q['caja']}</div>
                <div class="caja-vendedor">👤 {q['vendedor']}</div>
            </div>
            <div class="caja-estado" style="background: {bg_c}; color: {color_c};">
                {icon_c} {estado_c}
            </div>
        </div>
        
        <div class="caja-body">
            <div class="caja-horario">
                <span>🕐 Apertura: <b>{q['apertura'].split(' ')[1] if q['apertura'] else 'N/A'}</b></span>
                <span>🕔 Cierre: <b>{q['cierre'].split(' ')[1] if q['cierre'] else 'N/A'}</b></span>
            </div>
            
            <div class="caja-detalle">
                <div class="detalle-row">
                    <span>💵 Efectivo Vendido</span>
                    <b>S/ {q['efectivo_ventas']:,.2f}</b>
                </div>
                <div class="detalle-row">
                    <span>📱 Yape/QR Vendido</span>
                    <b>S/ {q['yape_ventas']:,.2f}</b>
                </div>
                <div class="detalle-row">
                    <span>💳 Tarjetas Vendido</span>
                    <b>S/ {q['tarjeta_ventas']:,.2f}</b>
                </div>
                <div class="detalle-row total-row">
                    <span>💰 TOTAL VENTAS</span>
                    <b>S/ {q['total_ventas']:,.2f}</b>
                </div>
                
                <div class="separador"></div>
                
                <div class="detalle-row">
                    <span>🏦 Saldo Inicial</span>
                    <b>S/ {q['saldo_inicial']:,.2f}</b>
                </div>
                <div class="detalle-row">
                    <span>🏦 Saldo Final</span>
                    <b>S/ {q['saldo_final']:,.2f}</b>
                </div>
                <div class="detalle-row diferencia-row" style="color: {dif_color};">
                    <span>⚖️ Diferencia Efectivo</span>
                    <b>{dif_signo}S/ {q['diferencia_efectivo']:,.2f}</b>
                </div>
            </div>
            
            <div class="caja-alertas">
                <div class="alerta-mini">
                    <div class="mini-label">Transacciones</div>
                    <div class="mini-value" style="color: #1E40AF;">{q['total_transacciones']}</div>
                </div>
                <div class="alerta-mini">
                    <div class="mini-label">🚨 Alertas</div>
                    <div class="mini-value" style="color: {'#DC2626' if q['alertas'] > 0 else '#059669'};">{q['alertas']}</div>
                </div>
                <div class="alerta-mini">
                    <div class="mini-label">💸 Monto Riesgo</div>
                    <div class="mini-value" style="color: {'#DC2626' if q['monto_alertas'] > 0 else '#059669'};">S/ {q['monto_alertas']:,.2f}</div>
                </div>
            </div>
        </div>
    </div>
    """

# TABLAS DE ALERTAS
def tabla_alertas_caja(df):
    if len(df) == 0:
        return '<div class="empty-state">✅ No hay ventas sospechosas</div>'
    rows = ""
    for _, r in df.iterrows():
        rows += f"""<tr>
            <td><span class="badge badge-caja">{r['Caja']}</span></td>
            <td><b>#{r['Op']}</b></td>
            <td>{r['Doc']}</td>
            <td><span class="badge badge-method">{r['Método']}</span></td>
            <td>{r['Hora Ref']}</td>
            <td class="monto-danger">S/ {r['Monto']:.2f}</td>
        </tr>"""
    return f"""<table class="tabla-alertas">
        <thead><tr><th>Caja</th><th>Op</th><th>Documento</th><th>Método</th><th>Hora</th><th>Monto</th></tr></thead>
        <tbody>{rows}</tbody></table>"""

def tabla_izipay_huerfanos(df):
    if len(df) == 0:
        return '<div class="empty-state">✅ Todos los cobros están registrados</div>'
    rows = ""
    for _, r in df.iterrows():
        rows += f"""<tr>
            <td>{r['Hora_str']}</td>
            <td><span class="badge badge-method">{r['Medio de cobro']}</span></td>
            <td class="monto-danger">S/ {r['Monto total']:.2f}</td>
            <td><span class="badge badge-danger">{r['Estado de venta']}</span></td>
        </tr>"""
    return f"""<table class="tabla-alertas">
        <thead><tr><th>Hora</th><th>Medio</th><th>Monto</th><th>Estado</th></tr></thead>
        <tbody>{rows}</tbody></table>"""

# Estado general
if riesgo_total < 10:
    estado_txt, estado_color, estado_icon = "SIN RIESGOS", "#059669", "✅"
elif riesgo_total < 200:
    estado_txt, estado_color, estado_icon = "RIESGO MODERADO", "#D97706", "⚠️"
else:
    estado_txt, estado_color, estado_icon = "RIESGO ALTO", "#DC2626", "🚨"

fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")

# ============================================================
# HTML COMPLETO
# ============================================================
html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard Gerencial | La Casa del Emprendedor</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
body {{ background: #F3F4F6; color: #111827; padding: 24px; min-height: 100vh; }}

.header {{ background: linear-gradient(135deg, #1E3A8A 0%, #3730A3 50%, #6D28D9 100%);
    color: white; padding: 32px 40px; border-radius: 20px; margin-bottom: 24px;
    box-shadow: 0 10px 40px rgba(30, 58, 138, 0.25); position: relative; overflow: hidden; }}
.header::before {{ content: ""; position: absolute; right: -50px; top: -50px; width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.1), transparent); border-radius: 50%; }}
.header-content {{ display: flex; justify-content: space-between; align-items: center; position: relative; z-index: 1; flex-wrap: wrap; gap: 16px; }}
.header h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 4px; }}
.header p {{ opacity: 0.9; font-size: 14px; }}
.header .fecha {{ background: rgba(255,255,255,0.15); padding: 12px 20px; border-radius: 12px; backdrop-filter: blur(10px); }}

.section-title {{ font-size: 20px; font-weight: 700; color: #111827; margin: 32px 0 16px 0; 
                  display: flex; align-items: center; gap: 10px; }}
.section-title::after {{ content: ""; flex: 1; height: 2px; background: linear-gradient(90deg, #6366F1, transparent); }}

.estado-banner {{ background: white; border-left: 6px solid {estado_color};
    padding: 20px 28px; border-radius: 14px; margin-bottom: 24px;
    display: flex; align-items: center; gap: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}
.estado-banner .icon {{ font-size: 42px; }}
.estado-banner .info {{ flex: 1; }}
.estado-banner .label {{ font-size: 12px; color: #6B7280; text-transform: uppercase; font-weight: 600; letter-spacing: 1px; }}
.estado-banner .value {{ font-size: 24px; font-weight: 800; color: {estado_color}; }}
.estado-banner .monto .num {{ font-size: 28px; font-weight: 800; color: {estado_color}; }}
.estado-banner .monto .lbl {{ font-size: 12px; color: #6B7280; }}

.kpis {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-bottom: 24px; }}
.kpi {{ background: white; padding: 22px; border-radius: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); transition: all 0.3s; border-top: 4px solid; }}
.kpi:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }}
.kpi .icon {{ font-size: 24px; margin-bottom: 8px; }}
.kpi .label {{ font-size: 11px; color: #6B7280; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }}
.kpi .value {{ font-size: 22px; font-weight: 800; color: #111827; margin-top: 6px; }}
.kpi .sub {{ font-size: 11px; color: #9CA3AF; margin-top: 4px; }}
.kpi.blue {{ border-color: #1E40AF; }} .kpi.green {{ border-color: #059669; }}
.kpi.purple {{ border-color: #7C3AED; }} .kpi.orange {{ border-color: #D97706; }}
.kpi.red {{ border-color: #DC2626; }} .kpi.cyan {{ border-color: #0891B2; }}

/* CAJAS QUIEBRES */
.cajas-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
.caja-card {{ background: white; border-radius: 16px; overflow: hidden;
              box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: transform 0.3s; }}
.caja-card:hover {{ transform: translateY(-4px); }}
.caja-header {{ padding: 20px 24px; color: white; display: flex; justify-content: space-between; align-items: center; }}
.caja-nombre {{ font-size: 22px; font-weight: 800; }}
.caja-vendedor {{ font-size: 13px; opacity: 0.9; margin-top: 4px; }}
.caja-estado {{ padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; }}
.caja-body {{ padding: 20px 24px; }}
.caja-horario {{ display: flex; justify-content: space-between; padding: 12px; background: #F9FAFB;
                 border-radius: 8px; margin-bottom: 16px; font-size: 13px; color: #4B5563; }}
.caja-detalle {{ margin-bottom: 16px; }}
.detalle-row {{ display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px; color: #4B5563; }}
.detalle-row b {{ color: #111827; }}
.total-row {{ border-top: 2px solid #E5E7EB; margin-top: 8px; padding-top: 12px;
              font-size: 16px; font-weight: 700; color: #111827; }}
.total-row b {{ color: #1E40AF; font-size: 18px; }}
.separador {{ height: 1px; background: #E5E7EB; margin: 12px 0; }}
.diferencia-row {{ padding: 10px; background: #FEF2F2; border-radius: 8px; font-weight: 600; margin-top: 8px; }}
.caja-alertas {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding-top: 16px; border-top: 1px solid #E5E7EB; }}
.alerta-mini {{ text-align: center; padding: 10px; background: #F9FAFB; border-radius: 8px; }}
.mini-label {{ font-size: 10px; color: #6B7280; text-transform: uppercase; font-weight: 600; }}
.mini-value {{ font-size: 18px; font-weight: 800; margin-top: 4px; }}

.charts-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }}
.chart-card {{ background: white; border-radius: 14px; padding: 16px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }}

.alertas-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
.alerta-card {{ background: white; border-radius: 14px; padding: 24px; 
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-top: 4px solid #DC2626; }}
.alerta-card.warning {{ border-top-color: #D97706; }}
.alerta-header {{ display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px; }}
.alerta-title {{ font-size: 16px; font-weight: 700; color: #111827; }}
.alerta-subtitle {{ font-size: 12px; color: #6B7280; margin-top: 4px; }}
.alerta-total {{ background: #FEE2E2; color: #DC2626; padding: 6px 14px; border-radius: 20px; 
                 font-weight: 700; font-size: 14px; white-space: nowrap; }}
.alerta-card.warning .alerta-total {{ background: #FEF3C7; color: #D97706; }}

.tabla-alertas {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }}
.tabla-alertas th {{ background: #F9FAFB; color: #374151; font-weight: 600; padding: 10px; 
                     text-align: left; text-transform: uppercase; font-size: 11px; border-bottom: 2px solid #E5E7EB; }}
.tabla-alertas td {{ padding: 12px 10px; border-bottom: 1px solid #F3F4F6; }}
.monto-danger {{ font-weight: 700; color: #DC2626; }}
.badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
.badge-caja {{ background: #DBEAFE; color: #1E40AF; }}
.badge-method {{ background: #EDE9FE; color: #6D28D9; }}
.badge-danger {{ background: #FEE2E2; color: #DC2626; }}
.empty-state {{ text-align: center; padding: 40px; color: #059669; font-weight: 600;
                background: #ECFDF5; border-radius: 10px; }}

.footer {{ text-align: center; padding: 24px; color: #6B7280; font-size: 12px; margin-top: 24px; }}

@media (max-width: 1200px) {{
    .kpis {{ grid-template-columns: repeat(3, 1fr); }}
    .charts-grid, .alertas-container, .cajas-container {{ grid-template-columns: 1fr; }}
}}
@media (max-width: 640px) {{
    body {{ padding: 12px; }}
    .kpis {{ grid-template-columns: repeat(2, 1fr); }}
    .header h1 {{ font-size: 22px; }}
}}
</style>
</head>
<body>

<div class="header">
    <div class="header-content">
        <div>
            <h1>📊 Dashboard Gerencial</h1>
            <p>La Casa del Emprendedor E.I.R.L. | RUC: 20615531627 | Av. Participación 509 - Loreto, Belén</p>
        </div>
        <div class="fecha">
            <div style="font-size:11px; opacity:0.8;">Reporte generado</div>
            <b>{fecha_hoy}</b>
        </div>
    </div>
</div>

<div class="estado-banner">
    <div class="icon">{estado_icon}</div>
    <div class="info">
        <div class="label">Estado General del Día</div>
        <div class="value">{estado_txt}</div>
    </div>
    <div class="monto">
        <div class="num">S/ {riesgo_total:.2f}</div>
        <div class="lbl">Monto en riesgo</div>
    </div>
</div>

<div class="kpis">
    <div class="kpi blue"><div class="icon">💰</div><div class="label">Ingreso Total</div>
        <div class="value">S/ {ingreso_total:,.2f}</div><div class="sub">{len(df_ventas)} transacciones</div></div>
    <div class="kpi green"><div class="icon">💵</div><div class="label">Efectivo</div>
        <div class="value">S/ {efectivo_total:,.2f}</div><div class="sub">{(efectivo_total/ingreso_total*100):.1f}% del total</div></div>
    <div class="kpi purple"><div class="icon">📱</div><div class="label">Digital (Caja)</div>
        <div class="value">S/ {digital_total:,.2f}</div><div class="sub">{len(df_digital)} transacciones</div></div>
    <div class="kpi cyan"><div class="icon">💳</div><div class="label">Cobrado Izipay</div>
        <div class="value">S/ {izipay_total:,.2f}</div><div class="sub">{len(df_izipay)} transacciones</div></div>
    <div class="kpi orange"><div class="icon">⚖️</div><div class="label">Diferencia</div>
        <div class="value">S/ {diferencia:,.2f}</div><div class="sub">Caja - Izipay</div></div>
    <div class="kpi red"><div class="icon">🚨</div><div class="label">Alertas</div>
        <div class="value">{len(alertas_caja) + len(izipay_huerf)}</div>
        <div class="sub">{len(alertas_caja)} caja + {len(izipay_huerf)} izipay</div></div>
</div>

<div class="section-title">🏪 Resumen de Quiebres por Caja</div>
<div class="cajas-container">
    {tarjeta_quiebre_caja(quiebre_c1)}
    {tarjeta_quiebre_caja(quiebre_c2)}
</div>

<div class="section-title">📊 Análisis Visual</div>
<div class="charts-grid">
    <div class="chart-card">{fig_hora.to_html(full_html=False, include_plotlyjs=False)}</div>
    <div class="chart-card">{fig_metodo.to_html(full_html=False, include_plotlyjs=False)}</div>
    <div class="chart-card">{fig_cajas.to_html(full_html=False, include_plotlyjs=False)}</div>
    <div class="chart-card">{fig_conc.to_html(full_html=False, include_plotlyjs=False)}</div>
</div>

<div class="section-title">🚨 Detalle de Alertas</div>
<div class="alertas-container">
    <div class="alerta-card">
        <div class="alerta-header">
            <div>
                <div class="alerta-title">🚨 Ventas en Caja SIN Cobro Izipay</div>
                <div class="alerta-subtitle">Posible fraude: se marcó digital pero no llegó el dinero</div>
            </div>
            <div class="alerta-total">S/ {monto_sospechoso:.2f}</div>
        </div>
        {tabla_alertas_caja(alertas_caja)}
    </div>
    <div class="alerta-card warning">
        <div class="alerta-header">
            <div>
                <div class="alerta-title">⚠️ Cobros Izipay SIN Registro en Caja</div>
                <div class="alerta-subtitle">Posible robo: llegó dinero pero no se emitió boleta</div>
            </div>
            <div class="alerta-total">S/ {monto_no_reg:.2f}</div>
        </div>
        {tabla_izipay_huerfanos(izipay_huerf)}
    </div>
</div>

<div class="footer">
    Dashboard generado automáticamente con Python 🐍 | Sistema de Control Anti-Fraude
</div>

</body>
</html>
"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard generado: dashboard.html")