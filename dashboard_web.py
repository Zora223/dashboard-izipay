import pdfplumber
import pandas as pd
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ============================================================
# EXTRAER DATOS DE CAJAS
# ============================================================
def extraer_caja(pdf_path, nombre_caja):
    resumen = {"caja": nombre_caja}
    metodos = {}
    
    with pdfplumber.open(pdf_path) as pdf:
        texto = pdf.pages[0].extract_text()
        vendedor = re.search(r"Vendedor:\s*(.+?)\s+Fecha", texto)
        ingreso = re.search(r"Ingreso caja:\s*S/\.\s*([\d,.]+)", texto)
        
        resumen["vendedor"] = vendedor.group(1) if vendedor else "N/A"
        resumen["ingreso_total"] = float(ingreso.group(1).replace(",", "")) if ingreso else 0
        
        for page in pdf.pages:
            for tabla in page.extract_tables():
                for fila in tabla:
                    if fila and len(fila) >= 3:
                        if fila[1] in ["Efectivo", "Yape", "Tarjeta de crédito", "Tarjeta de débito"]:
                            try:
                                metodos[fila[1]] = float(fila[2].replace(",", ""))
                            except:
                                pass
    resumen["metodos"] = metodos
    return resumen

# ============================================================
# CARGAR DATOS
# ============================================================
print("🔄 Procesando datos...")
c1 = extraer_caja("caja1.pdf", "Caja 1")
c2 = extraer_caja("caja2.pdf", "Caja 2")

df_izipay = pd.read_excel("izipay.xlsx")
df_izipay["Fecha y hora"] = pd.to_datetime(df_izipay["Fecha y hora"], dayfirst=True)
df_izipay["Hora"] = df_izipay["Fecha y hora"].dt.hour

# Totales
total_efectivo = c1["metodos"].get("Efectivo", 0) + c2["metodos"].get("Efectivo", 0)
total_yape_cajas = c1["metodos"].get("Yape", 0) + c2["metodos"].get("Yape", 0)
total_tarjeta_cajas = (c1["metodos"].get("Tarjeta de crédito", 0) + 
                       c1["metodos"].get("Tarjeta de débito", 0) +
                       c2["metodos"].get("Tarjeta de crédito", 0) + 
                       c2["metodos"].get("Tarjeta de débito", 0))
total_digital_cajas = total_yape_cajas + total_tarjeta_cajas
total_izipay = df_izipay["Monto total"].sum()
diferencia = total_digital_cajas - total_izipay

# Totales Izipay por método
izipay_qr = df_izipay[df_izipay["Medio de cobro"] == "sQR"]["Monto total"].sum()
izipay_tarjeta = df_izipay[df_izipay["Medio de cobro"] == "Pago con tarjeta celular"]["Monto total"].sum()

# ============================================================
# CREAR DASHBOARD HTML
# ============================================================
print("🎨 Generando dashboard...")

color_ok = "#10B981"
color_alerta = "#EF4444"
color_neutral = "#3B82F6"

estado_color = color_ok if abs(diferencia) < 1 else color_alerta
estado_texto = "✅ TODO OK" if abs(diferencia) < 1 else "🚨 REVISAR"

# Gráfico 1: Comparación Cajas vs Izipay
fig1 = go.Figure(data=[
    go.Bar(name='Cajas (POS)', x=['Yape/QR', 'Tarjetas'], 
           y=[total_yape_cajas, total_tarjeta_cajas],
           marker_color='#3B82F6', text=[f'S/ {total_yape_cajas:.2f}', f'S/ {total_tarjeta_cajas:.2f}'],
           textposition='auto'),
    go.Bar(name='Izipay', x=['Yape/QR', 'Tarjetas'], 
           y=[izipay_qr, izipay_tarjeta],
           marker_color='#F59E0B', text=[f'S/ {izipay_qr:.2f}', f'S/ {izipay_tarjeta:.2f}'],
           textposition='auto')
])
fig1.update_layout(title='💰 Comparación Cajas vs Izipay', barmode='group', 
                   template='plotly_white', height=400)

# Gráfico 2: Ventas por hora (Izipay)
ventas_hora = df_izipay.groupby("Hora")["Monto total"].sum().reset_index()
fig2 = px.bar(ventas_hora, x="Hora", y="Monto total", 
              title="📈 Ventas por Hora (Izipay)",
              color="Monto total", color_continuous_scale="Blues",
              text="Monto total")
fig2.update_traces(texttemplate='S/ %{text:.0f}', textposition='outside')
fig2.update_layout(template='plotly_white', height=400)

# Gráfico 3: Distribución métodos (todas las cajas)
metodos_totales = {
    "Efectivo": total_efectivo,
    "Yape/QR": total_yape_cajas,
    "Tarjetas": total_tarjeta_cajas
}
fig3 = go.Figure(data=[go.Pie(labels=list(metodos_totales.keys()), 
                              values=list(metodos_totales.values()),
                              hole=.4,
                              marker_colors=['#10B981', '#8B5CF6', '#F59E0B'])])
fig3.update_layout(title="🥧 Distribución Total de Métodos de Pago", 
                   template='plotly_white', height=400)

# Gráfico 4: Comparación por caja
fig4 = go.Figure(data=[
    go.Bar(name='Caja 1', x=['Efectivo', 'Yape', 'Tarj. Créd', 'Tarj. Déb'], 
           y=[c1["metodos"].get("Efectivo", 0), c1["metodos"].get("Yape", 0),
              c1["metodos"].get("Tarjeta de crédito", 0), c1["metodos"].get("Tarjeta de débito", 0)],
           marker_color='#3B82F6'),
    go.Bar(name='Caja 2', x=['Efectivo', 'Yape', 'Tarj. Créd', 'Tarj. Déb'], 
           y=[c2["metodos"].get("Efectivo", 0), c2["metodos"].get("Yape", 0),
              c2["metodos"].get("Tarjeta de crédito", 0), c2["metodos"].get("Tarjeta de débito", 0)],
           marker_color='#EF4444')
])
fig4.update_layout(title='🏪 Comparación por Caja', barmode='group', 
                   template='plotly_white', height=400)

# ============================================================
# HTML FINAL
# ============================================================
html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dashboard Gerencial - La Casa del Emprendedor</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }}
        body {{ background: #F3F4F6; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1E3A8A, #3B82F6); color: white; 
                   padding: 30px; border-radius: 15px; margin-bottom: 20px; text-align: center; }}
        .header h1 {{ font-size: 28px; margin-bottom: 5px; }}
        .header p {{ opacity: 0.9; }}
        .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                 gap: 15px; margin-bottom: 20px; }}
        .kpi {{ background: white; padding: 20px; border-radius: 10px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 4px solid #3B82F6; }}
        .kpi h3 {{ font-size: 13px; color: #6B7280; margin-bottom: 8px; text-transform: uppercase; }}
        .kpi .valor {{ font-size: 24px; font-weight: bold; color: #111827; }}
        .kpi.alerta {{ border-left-color: {estado_color}; }}
        .kpi.alerta .valor {{ color: {estado_color}; }}
        .charts {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .chart {{ background: white; padding: 15px; border-radius: 10px; 
                  box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        @media (max-width: 900px) {{ .charts {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Dashboard Gerencial - Control Anti-Fraude</h1>
        <p>La Casa del Emprendedor E.I.R.L. | RUC: 20615531627</p>
        <p>📅 Fecha: 25/07/2026</p>
    </div>
    
    <div class="kpis">
        <div class="kpi">
            <h3>💰 Ingreso Total</h3>
            <div class="valor">S/ {(c1["ingreso_total"] + c2["ingreso_total"]):.2f}</div>
        </div>
        <div class="kpi">
            <h3>💵 Total Efectivo</h3>
            <div class="valor">S/ {total_efectivo:.2f}</div>
        </div>
        <div class="kpi">
            <h3>💳 Digital en Cajas</h3>
            <div class="valor">S/ {total_digital_cajas:.2f}</div>
        </div>
        <div class="kpi">
            <h3>📱 Total Izipay</h3>
            <div class="valor">S/ {total_izipay:.2f}</div>
        </div>
        <div class="kpi alerta">
            <h3>⚠️ Diferencia</h3>
            <div class="valor">S/ {diferencia:.2f}</div>
        </div>
        <div class="kpi alerta">
            <h3>🎯 Estado</h3>
            <div class="valor">{estado_texto}</div>
        </div>
    </div>
    
    <div class="charts">
        <div class="chart">{fig1.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="chart">{fig3.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="chart">{fig2.to_html(full_html=False, include_plotlyjs=False)}</div>
        <div class="chart">{fig4.to_html(full_html=False, include_plotlyjs=False)}</div>
    </div>
</body>
</html>
"""

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("\n✅ Dashboard generado: dashboard.html")
print("🌐 Ábrelo con doble clic o desde el navegador")