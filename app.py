import streamlit as st
import pandas as pd
import pdfplumber
import re
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
import json

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(
    page_title="Dashboard Gerencial | La Casa del Emprendedor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS PREMIUM
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
    #MainMenu, footer { visibility: hidden; }
    
    /* Header transparente pero visible (para poder abrir el sidebar) */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 0px;
    }

    /* Botón de flecha para abrir sidebar - siempre visible */
    button[data-testid="stBaseButton-headerNoPadding"],
    button[kind="header"],
    [data-testid="stSidebarCollapsedControl"] {
        display: block !important;
        visibility: visible !important;
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
        color: #1E293B !important;
        z-index: 999999 !important;
        position: fixed !important;
        top: 15px !important;
        left: 15px !important;
        padding: 8px !important;
    }
    button[data-testid="stBaseButton-headerNoPadding"]:hover,
    [data-testid="stSidebarCollapsedControl"]:hover {
        background: #F3F4F6 !important;
        border-color: #8B5CF6 !important;
    }
    
    /* FONDO PRINCIPAL CLARO */
    .stApp { background: #F3F4F6 !important; }
    .main { background: #F3F4F6 !important; }
    
    /* HEADER */
    .header-premium {
        background: linear-gradient(135deg, #1E3A8A 0%, #3730A3 50%, #6D28D9 100%);
        color: white; padding: 32px 40px; border-radius: 20px; margin-bottom: 24px;
        box-shadow: 0 10px 40px rgba(30, 58, 138, 0.25);
        position: relative; overflow: hidden;
    }
    .header-premium::before {
        content: ""; position: absolute; right: -50px; top: -50px;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1), transparent);
        border-radius: 50%;
    }
    .header-premium h1 { font-size: 32px; font-weight: 800; margin: 0; color: white; }
    .header-premium p { opacity: 0.9; font-size: 14px; margin: 4px 0 0 0; color: white; }
    
    /* SEMÁFORO */
    .semaforo {
        background: white; padding: 20px 28px; border-radius: 14px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .semaforo-ok { border-left: 6px solid #059669; }
    .semaforo-warn { border-left: 6px solid #D97706; }
    .semaforo-danger { border-left: 6px solid #DC2626; }
    
    /* KPIs */
    .kpi-card {
        background: white; padding: 22px; border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-top: 4px solid #1E40AF;
        transition: all 0.3s;
        height: 100%;
    }
    .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.1); }
    .kpi-icon { font-size: 24px; margin-bottom: 8px; }
    .kpi-label { font-size: 11px; color: #6B7280; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .kpi-value { font-size: 22px; font-weight: 800; color: #111827; margin-top: 6px; }
    .kpi-sub { font-size: 11px; color: #9CA3AF; margin-top: 4px; }
    
    /* CAJAS */
    .caja-card {
        background: white; border-radius: 16px; overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .caja-header {
        padding: 20px 24px; color: white;
        display: flex; justify-content: space-between; align-items: center;
    }
    .caja-nombre { font-size: 22px; font-weight: 800; }
    .caja-vendedor { font-size: 13px; opacity: 0.9; margin-top: 4px; }
    .caja-estado {
        padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px;
        background: white;
    }
    .caja-body { padding: 20px 24px; }
    .caja-horario {
        display: flex; justify-content: space-between; padding: 12px;
        background: #F9FAFB; border-radius: 8px; margin-bottom: 16px;
        font-size: 13px; color: #4B5563;
    }
    .detalle-row {
        display: flex; justify-content: space-between; padding: 8px 0;
        font-size: 14px; color: #4B5563;
    }
    .detalle-row b { color: #111827; }
    .total-row {
        border-top: 2px solid #E5E7EB; margin-top: 8px; padding-top: 12px;
        font-size: 16px; font-weight: 700; color: #111827;
    }
    .total-row b { color: #1E40AF; font-size: 18px; }
    .diferencia-row {
        padding: 10px; background: #FEF2F2; border-radius: 8px;
        font-weight: 600; margin-top: 8px;
    }
    .separador { height: 1px; background: #E5E7EB; margin: 12px 0; }
    .mini-cards { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; padding-top: 16px; border-top: 1px solid #E5E7EB; }
    .mini-card { text-align: center; padding: 10px; background: #F9FAFB; border-radius: 8px; }
    .mini-label { font-size: 10px; color: #6B7280; text-transform: uppercase; font-weight: 600; }
    .mini-value { font-size: 18px; font-weight: 800; margin-top: 4px; }
    
    .section-title {
        font-size: 20px; font-weight: 700; color: #111827;
        margin: 24px 0 16px 0; display: flex; align-items: center; gap: 10px;
    }
    
    /* SIDEBAR SUAVE Y ELEGANTE */
    section[data-testid="stSidebar"] {
        background: #FAFBFC !important;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] > div {
        background: #FAFBFC !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: white !important;
        border: none;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
        transition: all 0.3s;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: white;
        color: #DC2626 !important;
        border: 1.5px solid #FCA5A5;
        box-shadow: none;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 12px;
        border: 1.5px dashed #D1D5DB;
        margin-bottom: 12px;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: #8B5CF6;
        background: #FAFAFF;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] small {
        color: #6B7280 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: #F3F4F6 !important;
        color: #4B5563 !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: none !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #E5E7EB;
    }
    
    /* FILTROS */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        border-color: #E5E7EB !important;
    }
    div[data-baseweb="tag"] {
        background-color: #EEF2FF !important;
        color: #4338CA !important;
    }
    div[data-baseweb="tag"] span {
        color: #4338CA !important;
    }
    .stMultiSelect label, .stMultiSelect > label > div {
        color: #1E293B !important;
        font-weight: 600 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #4B5563 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #EEF2FF !important;
        color: #4338CA !important;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# BASE DE DATOS LOCAL
# ============================================================
DB_FILE = "historial.json"

def cargar_historial():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"ventas": [], "izipay": [], "cajas": []}

def guardar_historial(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ============================================================
# FUNCIONES EXTRACCIÓN
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

def extraer_ventas_pdf(pdf_file, nombre_caja):
    ventas = []
    resumen = {}
    with pdfplumber.open(pdf_file) as pdf:
        texto = pdf.pages[0].extract_text()
        vendedor = re.search(r"Vendedor:\s*(.+?)\s+Fecha", texto)
        fecha_rep = re.search(r"Fecha reporte:\s*(\S+)", texto)
        ingreso = re.search(r"Ingreso caja:\s*S/\.\s*([\d,.]+)", texto)
        efectivo = re.search(r"Total efectivo:\s*S/\s*([\d,.]+)", texto)
        saldo_i = re.search(r"Saldo inicial:\s*S/\.\s*([\d,.]+)", texto)
        saldo_f = re.search(r"Saldo final:\s*S/\.\s*([\d,.]+)", texto)
        apertura = re.search(r"apertura:\s*(.+?)\n", texto)
        cierre = re.search(r"cierre:\s*(.+?)\n", texto)
        
        resumen = {
            "caja": nombre_caja,
            "vendedor": vendedor.group(1) if vendedor else "N/A",
            "fecha": fecha_rep.group(1) if fecha_rep else "N/A",
            "apertura": apertura.group(1) if apertura else "",
            "cierre": cierre.group(1) if cierre else "",
            "ingreso_total": float(ingreso.group(1).replace(",", "")) if ingreso else 0,
            "total_efectivo": float(efectivo.group(1).replace(",", "")) if efectivo else 0,
            "saldo_inicial": float(saldo_i.group(1).replace(",", "")) if saldo_i else 0,
            "saldo_final": float(saldo_f.group(1).replace(",", "")) if saldo_f else 0,
        }
        
        for page in pdf.pages:
            for tabla in page.extract_tables():
                for fila in tabla:
                    if fila and len(fila) >= 12 and fila[1] == "Venta":
                        try:
                            metodo, hora_ref, origen = parsear_metodo_pago(fila[2] or "")
                            ventas.append({
                                "fecha": resumen["fecha"],
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

def h2m(h):
    if not isinstance(h, str): return None
    try:
        a, b = map(int, h.split(":"))
        return a * 60 + b
    except: return None

def conciliar(df_digital, df_izipay):
    df_izipay = df_izipay.copy()
    df_izipay["Usado"] = False
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
        izi_h, izi_m = "-", "-"
        if match is not None:
            df_izipay.at[match, "Usado"] = True
            estado = "✅ OK" if diff <= 2 else f"⚠️ ±{diff}min"
            izi_h = df_izipay.loc[match, "Hora_str"]
            izi_m = f"S/ {df_izipay.loc[match, 'Monto total']:.2f}"
        resultados.append({
            "Fecha": v.get("fecha", ""), "Caja": v["caja"], "Op": v["n_op"],
            "Doc": v["documento"], "Método": v["metodo_pago"],
            "Hora Ref": v["hora_referencia"] or "-", "Monto": v["monto_pagado"],
            "Estado": estado, "Izipay Hora": izi_h, "Izipay Monto": izi_m
        })
    return pd.DataFrame(resultados), df_izipay

# ============================================================
# HEADER
# ============================================================
fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
st.markdown(f"""
<div class="header-premium">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div style="position:relative; z-index:1;">
            <h1>📊 Dashboard Gerencial</h1>
            <p>La Casa del Emprendedor E.I.R.L. | RUC: 20615531627 | Av. Participación 509 - Loreto, Belén</p>
        </div>
        <div style="background:rgba(255,255,255,0.15); padding:12px 20px; border-radius:12px; backdrop-filter:blur(10px); position:relative; z-index:1;">
            <div style="font-size:11px; opacity:0.8;">Reporte generado</div>
            <b style="font-size:16px;">{fecha_hoy}</b>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### 📤 Cargar Nuevos Datos")
    
    pdfs_uploaded = st.file_uploader("📄 PDFs de Caja", type=["pdf"], accept_multiple_files=True)
    excel_uploaded = st.file_uploader("📊 Excel de Izipay", type=["xlsx", "xls"])
    
    if st.button("💾 Procesar y Guardar", type="primary", use_container_width=True):
        if pdfs_uploaded or excel_uploaded:
            data = cargar_historial()
            
            if pdfs_uploaded:
                for i, pdf_file in enumerate(pdfs_uploaded):
                    nombre_caja = f"Caja {i+1}"
                    if "1" in pdf_file.name: nombre_caja = "Caja 1"
                    elif "2" in pdf_file.name: nombre_caja = "Caja 2"
                    elif "3" in pdf_file.name: nombre_caja = "Caja 3"
                    
                    resumen, ventas = extraer_ventas_pdf(pdf_file, nombre_caja)
                    
                    data["ventas"] = [v for v in data["ventas"] 
                                     if not (v["fecha"] == resumen["fecha"] and v["caja"] == nombre_caja)]
                    data["cajas"] = [c for c in data["cajas"] 
                                    if not (c["fecha"] == resumen["fecha"] and c["caja"] == nombre_caja)]
                    
                    data["ventas"].extend(ventas)
                    data["cajas"].append(resumen)
                    st.success(f"✅ {pdf_file.name}: {len(ventas)} ventas")
            
            if excel_uploaded:
                df_izi = pd.read_excel(excel_uploaded)
                df_izi["Fecha y hora"] = pd.to_datetime(df_izi["Fecha y hora"], dayfirst=True)
                
                fechas_nuevas = df_izi["Fecha y hora"].dt.date.unique()
                data["izipay"] = [i for i in data["izipay"] 
                                 if pd.to_datetime(i["fecha_hora"]).date() not in fechas_nuevas]
                
                for _, row in df_izi.iterrows():
                    data["izipay"].append({
                        "fecha_hora": row["Fecha y hora"].isoformat(),
                        "medio": row["Medio de cobro"],
                        "estado": row["Estado de venta"],
                        "monto": float(row["Monto total"]),
                        "tienda": row["Tienda"]
                    })
                st.success(f"✅ Izipay: {len(df_izi)} trans")
            
            guardar_historial(data)
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Sube archivos")
    
    st.divider()
    
    if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary"):
        if st.session_state.get("confirmar", False):
            guardar_historial({"ventas": [], "izipay": [], "cajas": []})
            st.session_state.confirmar = False
            st.rerun()
        else:
            st.session_state.confirmar = True
            st.warning("⚠️ Presiona de nuevo")

# ============================================================
# CARGAR DATOS
# ============================================================
data = cargar_historial()
df_ventas = pd.DataFrame(data["ventas"])
df_izipay_raw = pd.DataFrame(data["izipay"])
lista_cajas = data.get("cajas", [])

if len(df_ventas) == 0 and len(df_izipay_raw) == 0:
    st.info("👈 **Comienza subiendo tus archivos desde el panel izquierdo**")
    st.markdown("""
    ### 📋 Instrucciones:
    1. Sube los **PDFs de caja** (uno por cajera)
    2. Sube el **Excel de Izipay** del día
    3. Presiona **"Procesar y Guardar"**
    4. Los datos se **acumulan por fecha automáticamente**
    5. Usa los **filtros** para analizar periodos específicos
    """)
    st.stop()

# Preparar Izipay
if len(df_izipay_raw) > 0:
    df_izipay_raw["fecha_hora"] = pd.to_datetime(df_izipay_raw["fecha_hora"])
    df_izipay_raw["Fecha"] = df_izipay_raw["fecha_hora"].dt.date.astype(str)
    df_izipay_raw["Hora"] = df_izipay_raw["fecha_hora"].dt.hour
    df_izipay_raw["Hora_str"] = df_izipay_raw["fecha_hora"].dt.strftime("%H:%M")
    df_izipay_raw["Hora_minutos"] = df_izipay_raw["fecha_hora"].dt.hour * 60 + df_izipay_raw["fecha_hora"].dt.minute
    df_izipay_raw["Monto total"] = df_izipay_raw["monto"]
    df_izipay_raw["Medio de cobro"] = df_izipay_raw["medio"]
    df_izipay_raw["Estado de venta"] = df_izipay_raw["estado"]

# ============================================================
# FILTROS
# ============================================================
st.markdown('<div class="section-title">🔍 Filtros</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    fechas_v = sorted(df_ventas["fecha"].unique()) if len(df_ventas) > 0 else []
    fechas_i = sorted(df_izipay_raw["Fecha"].unique()) if len(df_izipay_raw) > 0 else []
    fechas_disp = sorted(set(list(fechas_v) + list(fechas_i)))
    fechas_sel = st.multiselect("📅 Fechas", fechas_disp, default=fechas_disp)

with col2:
    cajas_disp = sorted(df_ventas["caja"].unique()) if len(df_ventas) > 0 else []
    cajas_sel = st.multiselect("🏪 Cajas", cajas_disp, default=cajas_disp)

with col3:
    metodos_disp = ["Efectivo", "Yape", "Tarjeta de crédito", "Tarjeta de débito"]
    metodos_sel = st.multiselect("💳 Métodos", metodos_disp, default=metodos_disp)

# Aplicar filtros
df_ventas_f = df_ventas[
    (df_ventas["fecha"].isin(fechas_sel)) &
    (df_ventas["caja"].isin(cajas_sel)) &
    (df_ventas["metodo_pago"].isin(metodos_sel))
] if len(df_ventas) > 0 else df_ventas

df_izipay_f = df_izipay_raw[df_izipay_raw["Fecha"].isin(fechas_sel)] if len(df_izipay_raw) > 0 else df_izipay_raw
df_digital = df_ventas_f[df_ventas_f["metodo_pago"].isin(["Yape", "Tarjeta de crédito", "Tarjeta de débito"])].copy()
cajas_filt = [c for c in lista_cajas if c["fecha"] in fechas_sel and c["caja"] in cajas_sel]

# ============================================================
# CÁLCULOS
# ============================================================
efectivo_total = df_ventas_f[df_ventas_f["metodo_pago"] == "Efectivo"]["monto_pagado"].sum()
digital_total = df_digital["monto_pagado"].sum()
izipay_total = df_izipay_f["Monto total"].sum() if len(df_izipay_f) > 0 else 0
ingreso_total = df_ventas_f["monto_pagado"].sum()
diferencia = digital_total - izipay_total

if len(df_digital) > 0 and len(df_izipay_f) > 0:
    df_res, df_izi_check = conciliar(df_digital, df_izipay_f)
    alertas_caja = df_res[df_res["Estado"].str.contains("SIN COBRO")]
    izipay_huerf = df_izi_check[~df_izi_check["Usado"]]
else:
    df_res = pd.DataFrame()
    alertas_caja = pd.DataFrame()
    izipay_huerf = pd.DataFrame()

monto_sospechoso = alertas_caja["Monto"].sum() if len(alertas_caja) > 0 else 0
monto_no_reg = izipay_huerf["Monto total"].sum() if len(izipay_huerf) > 0 else 0
riesgo_total = monto_sospechoso + monto_no_reg

# ============================================================
# SEMÁFORO
# ============================================================
if riesgo_total < 10:
    est_txt, est_color, est_icon, est_class = "SIN RIESGOS", "#059669", "✅", "semaforo-ok"
elif riesgo_total < 200:
    est_txt, est_color, est_icon, est_class = "RIESGO MODERADO", "#D97706", "⚠️", "semaforo-warn"
else:
    est_txt, est_color, est_icon, est_class = "RIESGO ALTO", "#DC2626", "🚨", "semaforo-danger"

st.markdown(f"""
<div class="semaforo {est_class}">
    <div style="font-size:42px;">{est_icon}</div>
    <div style="flex:1;">
        <div style="font-size:12px; color:#6B7280; text-transform:uppercase; font-weight:600;">Estado General</div>
        <div style="font-size:24px; font-weight:800; color:{est_color};">{est_txt}</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:28px; font-weight:800; color:{est_color};">S/ {riesgo_total:,.2f}</div>
        <div style="font-size:12px; color:#6B7280;">Monto en riesgo</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPIs
# ============================================================
pct_efectivo = (efectivo_total/ingreso_total*100) if ingreso_total > 0 else 0

kpis_html = f"""
<div style="display:grid; grid-template-columns:repeat(6,1fr); gap:16px; margin-bottom:24px;">
    <div class="kpi-card" style="border-top-color:#1E40AF;">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Ingreso Total</div>
        <div class="kpi-value">S/ {ingreso_total:,.2f}</div>
        <div class="kpi-sub">{len(df_ventas_f)} transacciones</div>
    </div>
    <div class="kpi-card" style="border-top-color:#059669;">
        <div class="kpi-icon">💵</div>
        <div class="kpi-label">Efectivo</div>
        <div class="kpi-value">S/ {efectivo_total:,.2f}</div>
        <div class="kpi-sub">{pct_efectivo:.1f}% del total</div>
    </div>
    <div class="kpi-card" style="border-top-color:#7C3AED;">
        <div class="kpi-icon">📱</div>
        <div class="kpi-label">Digital (Caja)</div>
        <div class="kpi-value">S/ {digital_total:,.2f}</div>
        <div class="kpi-sub">{len(df_digital)} transacciones</div>
    </div>
    <div class="kpi-card" style="border-top-color:#0891B2;">
        <div class="kpi-icon">💳</div>
        <div class="kpi-label">Cobrado Izipay</div>
        <div class="kpi-value">S/ {izipay_total:,.2f}</div>
        <div class="kpi-sub">{len(df_izipay_f)} transacciones</div>
    </div>
    <div class="kpi-card" style="border-top-color:#D97706;">
        <div class="kpi-icon">⚖️</div>
        <div class="kpi-label">Diferencia</div>
        <div class="kpi-value">S/ {diferencia:,.2f}</div>
        <div class="kpi-sub">Caja - Izipay</div>
    </div>
    <div class="kpi-card" style="border-top-color:#DC2626;">
        <div class="kpi-icon">🚨</div>
        <div class="kpi-label">Alertas</div>
        <div class="kpi-value">{len(alertas_caja) + len(izipay_huerf)}</div>
        <div class="kpi-sub">{len(alertas_caja)} caja + {len(izipay_huerf)} izipay</div>
    </div>
</div>
"""
st.markdown(kpis_html, unsafe_allow_html=True)

# ============================================================
# RESUMEN DE QUIEBRES POR CAJA
# ============================================================
st.markdown('<div class="section-title">🏪 Resumen de Quiebres por Caja</div>', unsafe_allow_html=True)

def tarjeta_caja(caja_info, ventas_caja, alertas_caja_df):
    df_v = ventas_caja
    ef = df_v[df_v["metodo_pago"] == "Efectivo"]["monto_pagado"].sum()
    yp = df_v[df_v["metodo_pago"] == "Yape"]["monto_pagado"].sum()
    tj = df_v[df_v["metodo_pago"].str.contains("Tarjeta")]["monto_pagado"].sum()
    total_v = ef + yp + tj
    
    alertas_c = alertas_caja_df[alertas_caja_df["Caja"] == caja_info["caja"]] if len(alertas_caja_df) > 0 else pd.DataFrame()
    monto_al = alertas_c["Monto"].sum() if len(alertas_c) > 0 else 0
    diff_ef = caja_info["saldo_final"] - (caja_info["saldo_inicial"] + ef)
    
    if len(alertas_c) == 0 and abs(diff_ef) < 1:
        est, col, ic = "SIN QUIEBRES", "#059669", "✅"
    elif monto_al < 100:
        est, col, ic = "REVISAR", "#D97706", "⚠️"
    else:
        est, col, ic = "CON QUIEBRES", "#DC2626", "🚨"
    
    dif_col = "#059669" if abs(diff_ef) < 1 else "#DC2626"
    dif_sig = "+" if diff_ef > 0 else ""
    
    apertura_h = caja_info["apertura"].split(" ")[1] if caja_info.get("apertura") and " " in caja_info["apertura"] else "N/A"
    cierre_h = caja_info["cierre"].split(" ")[1] if caja_info.get("cierre") and " " in caja_info["cierre"] else "N/A"
    
    return f"""
    <div class="caja-card">
        <div class="caja-header" style="background:linear-gradient(135deg,{col},{col}dd);">
            <div>
                <div class="caja-nombre">🏪 {caja_info["caja"]}</div>
                <div class="caja-vendedor">👤 {caja_info["vendedor"]} | 📅 {caja_info["fecha"]}</div>
            </div>
            <div class="caja-estado" style="color:{col};">{ic} {est}</div>
        </div>
        <div class="caja-body">
            <div class="caja-horario">
                <span>🕐 Apertura: <b>{apertura_h}</b></span>
                <span>🕔 Cierre: <b>{cierre_h}</b></span>
            </div>
            <div class="detalle-row"><span>💵 Efectivo Vendido</span><b>S/ {ef:,.2f}</b></div>
            <div class="detalle-row"><span>📱 Yape/QR Vendido</span><b>S/ {yp:,.2f}</b></div>
            <div class="detalle-row"><span>💳 Tarjetas Vendido</span><b>S/ {tj:,.2f}</b></div>
            <div class="detalle-row total-row"><span>💰 TOTAL VENTAS</span><b>S/ {total_v:,.2f}</b></div>
            <div class="separador"></div>
            <div class="detalle-row"><span>🏦 Saldo Inicial</span><b>S/ {caja_info["saldo_inicial"]:,.2f}</b></div>
            <div class="detalle-row"><span>🏦 Saldo Final</span><b>S/ {caja_info["saldo_final"]:,.2f}</b></div>
            <div class="detalle-row diferencia-row" style="color:{dif_col};">
                <span>⚖️ Diferencia Efectivo</span><b>{dif_sig}S/ {diff_ef:,.2f}</b>
            </div>
            <div class="mini-cards">
                <div class="mini-card">
                    <div class="mini-label">Transacciones</div>
                    <div class="mini-value" style="color:#1E40AF;">{len(df_v)}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">🚨 Alertas</div>
                    <div class="mini-value" style="color:{'#DC2626' if len(alertas_c) > 0 else '#059669'};">{len(alertas_c)}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">💸 Monto Riesgo</div>
                    <div class="mini-value" style="color:{'#DC2626' if monto_al > 0 else '#059669'};">S/ {monto_al:,.2f}</div>
                </div>
            </div>
        </div>
    </div>
    """

if len(cajas_filt) > 0:
    cajas_html_list = []
    for caja_info in cajas_filt:
        ventas_c = df_ventas_f[(df_ventas_f["caja"] == caja_info["caja"]) & 
                                (df_ventas_f["fecha"] == caja_info["fecha"])]
        if len(ventas_c) > 0:
            cajas_html_list.append(tarjeta_caja(caja_info, ventas_c, alertas_caja))
    
    for i in range(0, len(cajas_html_list), 2):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(cajas_html_list[i], unsafe_allow_html=True)
        if i+1 < len(cajas_html_list):
            with col2:
                st.markdown(cajas_html_list[i+1], unsafe_allow_html=True)

# ============================================================
# GRÁFICOS
# ============================================================
st.markdown('<div class="section-title">📊 Análisis Visual</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if len(df_izipay_f) > 0:
        vh = df_izipay_f.groupby("Hora")["Monto total"].sum().reset_index()
        vh = vh.sort_values("Hora")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=vh["Hora"].astype(str), y=vh["Monto total"],
            marker=dict(color=vh["Monto total"], colorscale=[[0, "#DBEAFE"], [1, "#1E40AF"]], showscale=False),
            text=[f"S/{v:.0f}" for v in vh["Monto total"]],
            textposition="outside"
        ))
        fig.update_layout(
            title="<b>📈 Flujo de Ventas por Hora - Izipay</b>",
            xaxis_title="Hora del día", yaxis_title="Monto (S/)",
            plot_bgcolor="white", paper_bgcolor="white",
            height=400, margin=dict(t=50, b=40)
        )
        st.plotly_chart(fig, use_container_width=True)

with col2:
    metodos = df_ventas_f.groupby("metodo_pago")["monto_pagado"].sum().reset_index()
    if len(metodos) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=metodos["metodo_pago"], values=metodos["monto_pagado"],
            hole=0.55,
            marker=dict(colors=["#059669", "#7C3AED", "#D97706", "#0891B2"], line=dict(color="white", width=3)),
            textinfo="label+percent"
        )])
        fig.update_layout(
            title="<b>🥧 Distribución por Método de Pago</b>",
            height=400, showlegend=False, paper_bgcolor="white",
            annotations=[dict(text=f"<b>S/ {ingreso_total:,.0f}</b><br><span style='font-size:11px;color:gray'>Total</span>",
                             x=0.5, y=0.5, font=dict(size=18), showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    if len(df_ventas_f) > 0:
        por_caja = df_ventas_f.groupby(["caja", "metodo_pago"])["monto_pagado"].sum().reset_index()
        fig = px.bar(por_caja, x="caja", y="monto_pagado", color="metodo_pago",
                     title="<b>🏪 Rendimiento por Caja</b>", barmode="group", text_auto='.0f',
                     color_discrete_map={"Efectivo": "#059669", "Yape": "#7C3AED",
                                        "Tarjeta de crédito": "#D97706", "Tarjeta de débito": "#0891B2"})
        fig.update_layout(height=400, plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    izi_qr = df_izipay_f[df_izipay_f["Medio de cobro"] == "sQR"]["Monto total"].sum() if len(df_izipay_f) > 0 else 0
    izi_tar = df_izipay_f[df_izipay_f["Medio de cobro"] != "sQR"]["Monto total"].sum() if len(df_izipay_f) > 0 else 0
    caja_yape = df_digital[df_digital["metodo_pago"] == "Yape"]["monto_pagado"].sum()
    caja_tar = df_digital[df_digital["metodo_pago"].str.contains("Tarjeta")]["monto_pagado"].sum()
    
    fig = go.Figure(data=[
        go.Bar(name='🏪 Caja', x=["Yape/QR", "Tarjetas"], y=[caja_yape, caja_tar],
               marker_color="#1E40AF", text=[f"S/{caja_yape:.2f}", f"S/{caja_tar:.2f}"], textposition='outside'),
        go.Bar(name='💳 Izipay', x=["Yape/QR", "Tarjetas"], y=[izi_qr, izi_tar],
               marker_color="#DC2626", text=[f"S/{izi_qr:.2f}", f"S/{izi_tar:.2f}"], textposition='outside')
    ])
    fig.update_layout(title="<b>⚖️ Conciliación: Caja vs Izipay</b>", barmode='group',
                     plot_bgcolor="white", paper_bgcolor="white", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# ALERTAS
# ============================================================
st.markdown('<div class="section-title">🚨 Detalle de Alertas</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([f"🚨 Caja sin Izipay ({len(alertas_caja)})", 
                             f"⚠️ Izipay sin Caja ({len(izipay_huerf)})", 
                             f"📋 Todas ({len(df_res)})"])

with tab1:
    if len(alertas_caja) > 0:
        st.error(f"⚠️ **{len(alertas_caja)} ventas sospechosas** por **S/ {monto_sospechoso:.2f}**")
        st.dataframe(alertas_caja, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No hay ventas sin cobro en Izipay")

with tab2:
    if len(izipay_huerf) > 0:
        st.warning(f"⚠️ **{len(izipay_huerf)} cobros sin registrar** por **S/ {monto_no_reg:.2f}**")
        st.dataframe(izipay_huerf[["Hora_str", "Medio de cobro", "Monto total", "Estado de venta"]],
                     use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos los cobros están registrados")

with tab3:
    if len(df_res) > 0:
        st.dataframe(df_res, use_container_width=True, hide_index=True)

# ============================================================
# DESCARGAR
# ============================================================
st.markdown('<div class="section-title">📥 Descargar Reportes</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    if len(df_ventas_f) > 0:
        csv = df_ventas_f.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Ventas (CSV)", csv, "ventas.csv", "text/csv", use_container_width=True)
with col2:
    if len(alertas_caja) > 0:
        csv = alertas_caja.to_csv(index=False).encode('utf-8')
        st.download_button("🚨 Alertas (CSV)", csv, "alertas.csv", "text/csv", use_container_width=True)
with col3:
    if len(izipay_huerf) > 0:
        csv = izipay_huerf.to_csv(index=False).encode('utf-8')
        st.download_button("⚠️ Huérfanos (CSV)", csv, "huerfanos.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.caption("Dashboard Gerencial | Sistema Anti-Fraude 🐍")