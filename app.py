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
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"
if "vista_detalle" not in st.session_state:
    st.session_state.vista_detalle = None

st.set_page_config(
    page_title="Dashboard Gerencial | La Casa del Emprendedor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state=st.session_state.sidebar_state
)

# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
    .main .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }
    #MainMenu, footer { visibility: hidden; }
    .stApp { background: #F3F4F6 !important; }
    .main { background: #F3F4F6 !important; }
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
    .semaforo {
        background: white; padding: 20px 28px; border-radius: 14px; margin-bottom: 24px;
        display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .semaforo-ok { border-left: 6px solid #059669; }
    .semaforo-warn { border-left: 6px solid #D97706; }
    .semaforo-danger { border-left: 6px solid #DC2626; }
    .caja-card {
        background: white; border-radius: 16px; overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    .caja-header {
        padding: 20px 24px; color: white;
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
    }
    .caja-nombre { font-size: 22px; font-weight: 800; }
    .caja-vendedor { font-size: 13px; opacity: 0.9; margin-top: 4px; }
    .caja-estado {
        padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px;
        background: white;
    }
    .caja-body { padding: 20px 24px; }
    .caja-horario {
        display: flex; justify-content: space-between; padding: 12px; flex-wrap: wrap; gap: 8px;
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
    .kpi-container { background: white; padding: 20px; border-radius: 14px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); border-top: 4px solid #1E40AF;
        transition: all 0.3s; height: 100%; }
    .kpi-container:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
    .kpi-icon { font-size: 22px; margin-bottom: 6px; }
    .kpi-label { font-size: 10px; color: #6B7280; text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
    .kpi-value { font-size: 20px; font-weight: 800; color: #111827; margin-top: 4px; }
    .kpi-sub { font-size: 10px; color: #9CA3AF; margin-top: 4px; }
    .stButton > button {
        font-size: 12px !important;
        padding: 4px 12px !important;
    }
    .detalle-header {
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white; padding: 24px; border-radius: 16px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
    }
    .detalle-header h2 { margin: 0; font-size: 26px; font-weight: 800; color: white; }
    .detalle-header p { margin: 8px 0 0 0; opacity: 0.9; font-size: 14px; color: white; }
    section[data-testid="stSidebar"] { background: #FAFBFC !important; border-right: 1px solid #E5E7EB; }
    section[data-testid="stSidebar"] > div { background: #FAFBFC !important; }
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: #1E293B !important; font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #6366F1, #8B5CF6);
        color: white !important; border: none; font-weight: 600;
        border-radius: 10px; padding: 10px 20px;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2);
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px); box-shadow: 0 6px 16px rgba(139, 92, 246, 0.35);
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background: white; color: #DC2626 !important;
        border: 1.5px solid #FCA5A5; box-shadow: none;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        background: white; border-radius: 12px; padding: 12px;
        border: 1.5px dashed #D1D5DB; margin-bottom: 12px;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover {
        border-color: #8B5CF6; background: #FAFAFF;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] small { color: #6B7280 !important; }
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
        background: #F3F4F6 !important; color: #4B5563 !important;
        border: 1px solid #E5E7EB !important; box-shadow: none !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] hr { border-color: #E5E7EB; }
    div[data-baseweb="select"] > div { background-color: white !important; border-color: #E5E7EB !important; }
    div[data-baseweb="tag"] { background-color: #EEF2FF !important; color: #4338CA !important; }
    div[data-baseweb="tag"] span { color: #4338CA !important; }
    .stMultiSelect label, .stMultiSelect > label > div { color: #1E293B !important; font-weight: 600 !important; }
    .stTabs [data-baseweb="tab-list"] { background: white; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #4B5563 !important; }
    .stTabs [aria-selected="true"] { background: #EEF2FF !important; color: #4338CA !important; border-radius: 8px; }
    @media (max-width: 900px) {
        .header-premium { padding: 20px 24px; }
        .header-premium h1 { font-size: 22px; }
        .header-premium p { font-size: 12px; }
        .kpi-value { font-size: 16px !important; }
        .kpi-label { font-size: 10px !important; }
        .semaforo { flex-direction: column; text-align: center; }
        .caja-nombre { font-size: 18px; }
        .section-title { font-size: 16px; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# BOTÓN TOGGLE SIDEBAR
# ============================================================
col_btn, col_space = st.columns([1, 10])
with col_btn:
    if st.button("📤 Panel", type="primary", use_container_width=True):
        st.session_state.sidebar_state = "expanded" if st.session_state.sidebar_state == "collapsed" else "collapsed"
        st.rerun()

# ============================================================
# BASE DE DATOS LOCAL
# ============================================================
DB_FILE = "historial.json"

def cargar_historial():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "yape" not in data: data["yape"] = []
            if "bcp" not in data: data["bcp"] = []
            if "justificaciones" not in data: data["justificaciones"] = {}
            return data
    return {"ventas": [], "izipay": [], "yape": [], "bcp": [], "cajas": [], "justificaciones": {}}

def guardar_historial(data):
    if "yape" not in data: data["yape"] = []
    if "bcp" not in data: data["bcp"] = []
    if "justificaciones" not in data: data["justificaciones"] = {}
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ============================================================
# FUNCIONES DE PARSEO
# ============================================================
def parsear_metodo_pago(texto_crudo):
    if not texto_crudo: return ("Desconocido", None, None, None)
    texto = texto_crudo.replace("\n", " ").strip()
    texto_lower = texto.lower()
    metodo = "Otro"
    if "yape" in texto_lower: metodo = "Yape"
    elif "tarjeta de\ncrédito" in texto_crudo.lower() or "tarjeta de crédito" in texto_lower: metodo = "Tarjeta de crédito"
    elif "tarjeta de\ndébito" in texto_crudo.lower() or "tarjeta de débito" in texto_lower: metodo = "Tarjeta de débito"
    elif "efectivo" in texto_lower: metodo = "Efectivo"
    origen = None
    m_o = re.search(r"\b(izi?|bcp|yape|plin|bim)\b", texto_lower)
    if m_o:
        val = m_o.group(1).upper()
        if val == "IZ": val = "IZI"
        origen = val
    num_op = None
    m_num = re.search(r"(?:izi?|bcp|yape|plin|bim)[\s/]+(\d{4,})", texto_lower)
    if m_num:
        num_op = m_num.group(1).lstrip("0")
    hora_ref = None
    if num_op is None:
        m_h = re.search(r"(\d{1,2}):(\d{2})", texto)
        if m_h:
            h, m = int(m_h.group(1)), int(m_h.group(2))
            if 0 <= h < 24 and 0 <= m < 60:
                hora_ref = f"{h:02d}:{m:02d}"
    return (metodo, hora_ref, origen, num_op)

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
                            metodo, hora_ref, origen, num_op = parsear_metodo_pago(fila[2] or "")
                            ventas.append({
                                "fecha": resumen["fecha"],
                                "caja": nombre_caja,
                                "vendedor": resumen["vendedor"],
                                "n_op": fila[0],
                                "metodo_pago": metodo,
                                "hora_referencia": hora_ref,
                                "origen_ref": origen,
                                "num_operacion": num_op,
                                "documento": fila[4],
                                "monto_pagado": float(fila[10].replace(",", "")) if fila[10] else 0,
                                "raw_metodo": (fila[2] or "").replace("\n", " ")
                            })
                        except: pass
    return resumen, ventas

def h2m(h):
    if not isinstance(h, str): return None
    try:
        a, b = map(int, h.split(":"))
        return a * 60 + b
    except: return None

def leer_yape(yape_file):
    df_temp = pd.read_excel(yape_file, header=None)
    header_row = None
    for i, row in df_temp.iterrows():
        valores = [str(v).lower() for v in row.values if pd.notna(v)]
        if any("tipo" in v and "transac" in v for v in valores):
            header_row = i
            break
    if header_row is None: return None
    df_y = pd.read_excel(yape_file, header=header_row)
    col_fecha = col_monto = col_tipo = None
    for c in df_y.columns:
        cl = str(c).lower().strip()
        if "fecha" in cl and col_fecha is None: col_fecha = c
        if "monto" in cl and col_monto is None: col_monto = c
        if "tipo" in cl and col_tipo is None: col_tipo = c
    if not (col_fecha and col_monto): return None
    df_y[col_fecha] = pd.to_datetime(df_y[col_fecha], dayfirst=True, errors='coerce')
    df_y = df_y.dropna(subset=[col_fecha])
    if col_tipo:
        df_y = df_y[df_y[col_tipo].astype(str).str.upper().str.contains("PAG", na=False)]
    df_y[col_monto] = pd.to_numeric(df_y[col_monto], errors='coerce')
    df_y = df_y.dropna(subset=[col_monto])
    return df_y, col_fecha, col_monto

def leer_bcp(bcp_file):
    df = pd.read_excel(bcp_file)
    col_fecha = col_monto = col_numop = col_desc = None
    for c in df.columns:
        cl = str(c).lower().strip()
        if "fecha" in cl and col_fecha is None: col_fecha = c
        if "monto" in cl and col_monto is None: col_monto = c
        if ("numero" in cl or "número" in cl or "operac" in cl) and col_numop is None: col_numop = c
        if "descrip" in cl and col_desc is None: col_desc = c
    if not (col_fecha and col_monto): return None
    df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors='coerce')
    df = df.dropna(subset=[col_fecha])
    df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce')
    df = df.dropna(subset=[col_monto])
    df = df[df[col_monto] > 0]
    df["es_venta"] = True
    if col_desc:
        patrones_no_venta = [
            "TRAN.CTAS.TERC", "SUNA", "DEPOSITO EFECTIVO",
            "COMISION", "MANT", "PORTES",
        ]
        mask_no_venta = df[col_desc].astype(str).str.upper().str.contains("|".join(patrones_no_venta), na=False)
        df.loc[mask_no_venta, "es_venta"] = False
    return df, col_fecha, col_monto, col_numop, col_desc

def conciliar_multi(df_digital, df_izipay, df_yape, df_bcp):
    df_izipay = df_izipay.copy() if len(df_izipay) > 0 else pd.DataFrame()
    df_yape = df_yape.copy() if len(df_yape) > 0 else pd.DataFrame()
    df_bcp = df_bcp.copy() if len(df_bcp) > 0 else pd.DataFrame()
    if len(df_izipay) > 0: df_izipay["Usado"] = False
    if len(df_yape) > 0: df_yape["Usado"] = False
    if len(df_bcp) > 0: df_bcp["Usado"] = False
    resultados = []
    for _, v in df_digital.iterrows():
        num_op = v.get("num_operacion")
        hm = h2m(v.get("hora_referencia"))
        monto = v["monto_pagado"]
        encontrado = None
        if num_op:
            if len(df_izipay) > 0 and encontrado is None:
                for idx, row in df_izipay[~df_izipay["Usado"]].iterrows():
                    for col in df_izipay.columns:
                        val = str(row.get(col, "")).lstrip("0")
                        if val == num_op and abs(row["Monto total"] - monto) <= 0.10:
                            df_izipay.at[idx, "Usado"] = True
                            encontrado = ("Izipay", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "-"))
                            break
                    if encontrado: break
            if len(df_yape) > 0 and encontrado is None:
                for idx, row in df_yape[~df_yape["Usado"]].iterrows():
                    for col in df_yape.columns:
                        val = str(row.get(col, "")).lstrip("0")
                        if val == num_op and abs(row["Monto total"] - monto) <= 0.10:
                            df_yape.at[idx, "Usado"] = True
                            encontrado = ("Yape", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "Yape"))
                            break
                    if encontrado: break
            if len(df_bcp) > 0 and encontrado is None:
                for idx, row in df_bcp[~df_bcp["Usado"]].iterrows():
                    num_bcp = str(row.get("num_operacion", "")).lstrip("0")
                    if num_bcp == num_op and abs(row["Monto total"] - monto) <= 0.10:
                        df_bcp.at[idx, "Usado"] = True
                        encontrado = ("BCP", row.get("Hora_str", "-"), row["Monto total"], row.get("descripcion", "BCP"))
                        break
        if encontrado is None and hm is not None:
            if len(df_izipay) > 0:
                for idx, row in df_izipay[~df_izipay["Usado"]].iterrows():
                    if abs(row["Monto total"] - monto) <= 0.10 and abs(row["Hora_minutos"] - hm) <= 10:
                        df_izipay.at[idx, "Usado"] = True
                        encontrado = ("Izipay", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "-"))
                        break
            if encontrado is None and len(df_yape) > 0:
                for idx, row in df_yape[~df_yape["Usado"]].iterrows():
                    if abs(row["Monto total"] - monto) <= 0.10 and abs(row["Hora_minutos"] - hm) <= 10:
                        df_yape.at[idx, "Usado"] = True
                        encontrado = ("Yape", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "Yape"))
                        break
        if encontrado is None and len(df_bcp) > 0:
            for idx, row in df_bcp[~df_bcp["Usado"]].iterrows():
                if abs(row["Monto total"] - monto) <= 0.10:
                    df_bcp.at[idx, "Usado"] = True
                    encontrado = ("BCP", row.get("Hora_str", "-"), row["Monto total"], row.get("descripcion", "BCP"))
                    break
        if encontrado is None:
            if len(df_izipay) > 0:
                for idx, row in df_izipay[~df_izipay["Usado"]].iterrows():
                    if abs(row["Monto total"] - monto) <= 0.10:
                        df_izipay.at[idx, "Usado"] = True
                        encontrado = ("Izipay*", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "-"))
                        break
            if encontrado is None and len(df_yape) > 0:
                for idx, row in df_yape[~df_yape["Usado"]].iterrows():
                    if abs(row["Monto total"] - monto) <= 0.10:
                        df_yape.at[idx, "Usado"] = True
                        encontrado = ("Yape*", row["Hora_str"], row["Monto total"], row.get("Medio de cobro", "Yape"))
                        break
        if encontrado:
            fuente, hora_e, monto_e, medio_e = encontrado
            estado = "✅ OK"
        else:
            fuente, hora_e, monto_e, medio_e = "-", "-", "-", "-"
            estado = "🚨 SIN COBRO"
        resultados.append({
            "Fecha": v.get("fecha", ""), "Caja": v["caja"], "Op": v["n_op"],
            "Doc": v["documento"], "Método": v["metodo_pago"],
            "Ref": v.get("raw_metodo", ""),
            "N° Op": num_op or "-",
            "Hora Ref": v["hora_referencia"] or "-", 
            "Monto": v["monto_pagado"],
            "Estado": estado, "Fuente": fuente,
            "Cobro Hora": hora_e,
            "Cobro Monto": f"S/ {monto_e:.2f}" if isinstance(monto_e, (int, float)) else monto_e,
        })
    return pd.DataFrame(resultados), df_izipay, df_yape, df_bcp

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
    excel_uploaded = st.file_uploader("📊 Excel de Izipay", type=["xlsx", "xls"], key="izipay_up")
    yape_uploaded = st.file_uploader("📱 Excel de Yape", type=["xlsx", "xls"], key="yape_up")
    bcp_uploaded = st.file_uploader("🏦 Excel de BCP", type=["xlsx", "xls"], key="bcp_up")
    
    if st.button("💾 Procesar y Guardar", type="primary", use_container_width=True):
        if pdfs_uploaded or excel_uploaded or yape_uploaded or bcp_uploaded:
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
                        "medio": row["Medio de cobro"], "estado": row["Estado de venta"],
                        "monto": float(row["Monto total"]), "tienda": row["Tienda"]
                    })
                st.success(f"✅ Izipay: {len(df_izi)} trans")
            if yape_uploaded:
                try:
                    result = leer_yape(yape_uploaded)
                    if result is None: st.error("❌ No se pudo leer Yape")
                    else:
                        df_y, col_fecha, col_monto = result
                        fechas_nuevas_y = df_y[col_fecha].dt.date.unique()
                        data["yape"] = [y for y in data["yape"] 
                                       if pd.to_datetime(y["fecha_hora"]).date() not in fechas_nuevas_y]
                        for _, row in df_y.iterrows():
                            data["yape"].append({
                                "fecha_hora": row[col_fecha].isoformat(),
                                "monto": float(row[col_monto]),
                            })
                        st.success(f"✅ Yape: {len(df_y)} trans")
                except Exception as e: st.error(f"❌ Error Yape: {str(e)}")
            if bcp_uploaded:
                try:
                    result = leer_bcp(bcp_uploaded)
                    if result is None: st.error("❌ No se pudo leer BCP")
                    else:
                        df_b, col_fecha, col_monto, col_numop, col_desc = result
                        fechas_nuevas_b = df_b[col_fecha].dt.date.unique()
                        data["bcp"] = [b for b in data["bcp"] 
                                      if pd.to_datetime(b["fecha_hora"]).date() not in fechas_nuevas_b]
                        for _, row in df_b.iterrows():
                            data["bcp"].append({
                                "fecha_hora": row[col_fecha].isoformat(),
                                "monto": float(row[col_monto]),
                                "num_operacion": str(row[col_numop]) if col_numop else "",
                                "descripcion": str(row[col_desc]) if col_desc else "",
                                "es_venta": bool(row["es_venta"]),
                            })
                        ventas_bcp = int(df_b["es_venta"].sum())
                        no_ventas_bcp = int((~df_b["es_venta"]).sum())
                        st.success(f"✅ BCP: {len(df_b)} trans ({ventas_bcp} ventas + {no_ventas_bcp} movimientos)")
                except Exception as e: st.error(f"❌ Error BCP: {str(e)}")
            guardar_historial(data)
            st.balloons()
            st.rerun()
        else: st.warning("⚠️ Sube archivos")
    st.divider()
    if st.button("🗑️ Limpiar Historial", use_container_width=True, type="secondary"):
        if st.session_state.get("confirmar", False):
            guardar_historial({"ventas": [], "izipay": [], "yape": [], "bcp": [], "cajas": [], "justificaciones": {}})
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
df_yape_raw = pd.DataFrame(data.get("yape", []))
df_bcp_raw = pd.DataFrame(data.get("bcp", []))
lista_cajas = data.get("cajas", [])
justificaciones = data.get("justificaciones", {})

if len(df_ventas) == 0:
    st.info("👈 **Comienza subiendo tus archivos desde el panel izquierdo**")
    st.stop()

if len(df_izipay_raw) > 0:
    df_izipay_raw["fecha_hora"] = pd.to_datetime(df_izipay_raw["fecha_hora"])
    df_izipay_raw["Fecha"] = df_izipay_raw["fecha_hora"].dt.date.astype(str)
    df_izipay_raw["Hora"] = df_izipay_raw["fecha_hora"].dt.hour
    df_izipay_raw["Hora_str"] = df_izipay_raw["fecha_hora"].dt.strftime("%H:%M")
    df_izipay_raw["Hora_minutos"] = df_izipay_raw["fecha_hora"].dt.hour * 60 + df_izipay_raw["fecha_hora"].dt.minute
    df_izipay_raw["Monto total"] = df_izipay_raw["monto"]
    df_izipay_raw["Medio de cobro"] = df_izipay_raw["medio"]
    df_izipay_raw["Estado de venta"] = df_izipay_raw["estado"]
if len(df_yape_raw) > 0:
    df_yape_raw["fecha_hora"] = pd.to_datetime(df_yape_raw["fecha_hora"])
    df_yape_raw["Fecha"] = df_yape_raw["fecha_hora"].dt.date.astype(str)
    df_yape_raw["Hora"] = df_yape_raw["fecha_hora"].dt.hour
    df_yape_raw["Hora_str"] = df_yape_raw["fecha_hora"].dt.strftime("%H:%M")
    df_yape_raw["Hora_minutos"] = df_yape_raw["fecha_hora"].dt.hour * 60 + df_yape_raw["fecha_hora"].dt.minute
    df_yape_raw["Monto total"] = df_yape_raw["monto"]
    df_yape_raw["Medio de cobro"] = "Yape"
if len(df_bcp_raw) > 0:
    df_bcp_raw["fecha_hora"] = pd.to_datetime(df_bcp_raw["fecha_hora"])
    df_bcp_raw["Fecha"] = df_bcp_raw["fecha_hora"].dt.date.astype(str)
    df_bcp_raw["Hora"] = df_bcp_raw["fecha_hora"].dt.hour
    df_bcp_raw["Hora_str"] = df_bcp_raw["fecha_hora"].dt.strftime("%H:%M")
    df_bcp_raw["Hora_minutos"] = df_bcp_raw["fecha_hora"].dt.hour * 60 + df_bcp_raw["fecha_hora"].dt.minute
    df_bcp_raw["Monto total"] = df_bcp_raw["monto"]
    df_bcp_raw["Medio de cobro"] = "BCP"
    if "es_venta" not in df_bcp_raw.columns:
        df_bcp_raw["es_venta"] = True

# ============================================================
# FILTROS
# ============================================================
st.markdown('<div class="section-title">🔍 Filtros</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    fechas_disp = sorted(df_ventas["fecha"].unique()) if len(df_ventas) > 0 else []
    fechas_sel = st.multiselect("📅 Fechas (según reporte de caja)", fechas_disp, default=fechas_disp)

with col2:
    cajas_disp = sorted(df_ventas["caja"].unique()) if len(df_ventas) > 0 else []
    cajas_sel = st.multiselect("🏪 Cajas", cajas_disp, default=cajas_disp)

with col3:
    metodos_disp = ["Efectivo", "Yape", "Tarjeta de crédito", "Tarjeta de débito"]
    metodos_sel = st.multiselect("💳 Métodos", metodos_disp, default=metodos_disp)

# ============================================================
# FILTRAR BASE
# ============================================================
df_ventas_base = df_ventas[
    (df_ventas["fecha"].isin(fechas_sel)) &
    (df_ventas["caja"].isin(cajas_sel))
] if len(df_ventas) > 0 else df_ventas

df_izipay_base = df_izipay_raw[df_izipay_raw["Fecha"].isin(fechas_sel)] if len(df_izipay_raw) > 0 else df_izipay_raw
df_yape_base = df_yape_raw[df_yape_raw["Fecha"].isin(fechas_sel)] if len(df_yape_raw) > 0 else df_yape_raw
df_bcp_base = df_bcp_raw[df_bcp_raw["Fecha"].isin(fechas_sel)] if len(df_bcp_raw) > 0 else df_bcp_raw
df_bcp_para_cruce = df_bcp_base[df_bcp_base["es_venta"] == True] if len(df_bcp_base) > 0 else df_bcp_base
cajas_filt = [c for c in lista_cajas if c["fecha"] in fechas_sel and c["caja"] in cajas_sel]

# ============================================================
# OPCIÓN D: DETECTAR DUPLICADOS YAPE-BCP ANTES DE CONCILIAR
# Si un cobro Yape coincide en monto con un BCP, es el mismo cobro
# Eliminamos el Yape porque el BCP tiene número de operación (más confiable)
# ============================================================
df_yape_para_cruce = df_yape_base.copy() if len(df_yape_base) > 0 else pd.DataFrame()
if len(df_yape_para_cruce) > 0 and len(df_bcp_para_cruce) > 0:
    montos_bcp = df_bcp_para_cruce["Monto total"].round(2).tolist()
    df_yape_para_cruce["es_duplicado_bcp"] = df_yape_para_cruce["Monto total"].round(2).apply(
        lambda m: m in montos_bcp
    )
    duplicados_removidos = df_yape_para_cruce["es_duplicado_bcp"].sum()
    df_yape_para_cruce = df_yape_para_cruce[df_yape_para_cruce["es_duplicado_bcp"] == False]
    df_yape_para_cruce = df_yape_para_cruce.drop(columns=["es_duplicado_bcp"])

# CONCILIACIÓN
df_digital_base = df_ventas_base[df_ventas_base["metodo_pago"].isin(
    ["Yape", "Tarjeta de crédito", "Tarjeta de débito"]
)].copy()

if len(df_digital_base) > 0:
    df_res_full, df_izi_check, df_yape_check, df_bcp_check = conciliar_multi(
        df_digital_base, df_izipay_base, df_yape_para_cruce, df_bcp_para_cruce
    )
    alertas_caja_full = df_res_full[df_res_full["Estado"].str.contains("SIN COBRO")]
    izipay_huerf_full = df_izi_check[~df_izi_check["Usado"]] if len(df_izi_check) > 0 else pd.DataFrame()
    yape_huerf_full = df_yape_check[~df_yape_check["Usado"]] if len(df_yape_check) > 0 else pd.DataFrame()
    bcp_huerf_full = df_bcp_check[~df_bcp_check["Usado"]] if len(df_bcp_check) > 0 else pd.DataFrame()
    
    # DETECTAR POSIBLES RELACIONES ENTRE ALERTAS Y HUÉRFANOS
    def buscar_relacion(monto, izi_huerf, yape_huerf, bcp_huerf):
        relaciones = []
        if len(izi_huerf) > 0:
            for _, row in izi_huerf.iterrows():
                if abs(row["Monto total"] - monto) <= 0.10:
                    relaciones.append(f"🔗 Izipay {row['Hora_str']} - S/ {row['Monto total']:.2f}")
        if len(yape_huerf) > 0:
            for _, row in yape_huerf.iterrows():
                if abs(row["Monto total"] - monto) <= 0.10:
                    relaciones.append(f"🔗 Yape {row['Hora_str']} - S/ {row['Monto total']:.2f}")
        if len(bcp_huerf) > 0:
            for _, row in bcp_huerf.iterrows():
                if abs(row["Monto total"] - monto) <= 0.10:
                    desc = str(row.get("descripcion", ""))[:30]
                    relaciones.append(f"🔗 BCP - S/ {row['Monto total']:.2f} ({desc})")
        return " | ".join(relaciones) if relaciones else ""
    
    if len(alertas_caja_full) > 0:
        alertas_caja_full = alertas_caja_full.copy()
        alertas_caja_full["Posible Relación"] = alertas_caja_full["Monto"].apply(
            lambda m: buscar_relacion(m, izipay_huerf_full, yape_huerf_full, bcp_huerf_full)
        )
else:
    df_res_full = pd.DataFrame()
    alertas_caja_full = pd.DataFrame()
    izipay_huerf_full = pd.DataFrame()
    yape_huerf_full = pd.DataFrame()
    bcp_huerf_full = pd.DataFrame()

df_ventas_f = df_ventas_base[df_ventas_base["metodo_pago"].isin(metodos_sel)] if len(df_ventas_base) > 0 else df_ventas_base
df_digital = df_ventas_f[df_ventas_f["metodo_pago"].isin(["Yape", "Tarjeta de crédito", "Tarjeta de débito"])].copy()
alertas_caja = alertas_caja_full[alertas_caja_full["Método"].isin(metodos_sel)] if len(alertas_caja_full) > 0 else pd.DataFrame()
df_res = df_res_full[df_res_full["Método"].isin(metodos_sel)] if len(df_res_full) > 0 else pd.DataFrame()
izipay_huerf = izipay_huerf_full
yape_huerf = yape_huerf_full if "Yape" in metodos_sel else pd.DataFrame()
bcp_huerf = bcp_huerf_full if "Yape" in metodos_sel else pd.DataFrame()
df_izipay_f = df_izipay_base
df_yape_f = df_yape_base if "Yape" in metodos_sel else pd.DataFrame()
df_bcp_f = df_bcp_base if "Yape" in metodos_sel else pd.DataFrame()

# CÁLCULOS
efectivo_total = df_ventas_f[df_ventas_f["metodo_pago"] == "Efectivo"]["monto_pagado"].sum() if len(df_ventas_f) > 0 else 0
digital_total = df_digital["monto_pagado"].sum() if len(df_digital) > 0 else 0
izipay_total = df_izipay_f["Monto total"].sum() if len(df_izipay_f) > 0 else 0
yape_total = df_yape_f["Monto total"].sum() if len(df_yape_f) > 0 else 0
bcp_total = df_bcp_f["Monto total"].sum() if len(df_bcp_f) > 0 else 0
ingreso_total = df_ventas_f["monto_pagado"].sum() if len(df_ventas_f) > 0 else 0
monto_sospechoso = alertas_caja["Monto"].sum() if len(alertas_caja) > 0 else 0
monto_no_reg_izi = izipay_huerf["Monto total"].sum() if len(izipay_huerf) > 0 else 0
monto_no_reg_yape = yape_huerf["Monto total"].sum() if len(yape_huerf) > 0 else 0
monto_no_reg_bcp = bcp_huerf["Monto total"].sum() if len(bcp_huerf) > 0 else 0
monto_no_reg = monto_no_reg_izi + monto_no_reg_yape + monto_no_reg_bcp
riesgo_total = monto_sospechoso + monto_no_reg

# SEMÁFORO
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
# KPIs CLICKEABLES
# ============================================================
st.markdown('<div class="section-title">📊 Indicadores Clave (Click en "Ver Detalle")</div>', unsafe_allow_html=True)

pct_efectivo = (efectivo_total/ingreso_total*100) if ingreso_total > 0 else 0
total_alertas = len(alertas_caja) + len(izipay_huerf) + len(yape_huerf) + len(bcp_huerf)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#1E40AF;">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Ingreso Total</div>
        <div class="kpi-value">S/ {ingreso_total:,.2f}</div>
        <div class="kpi-sub">{len(df_ventas_f)} trans</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_ingreso", use_container_width=True):
        st.session_state.vista_detalle = "ingreso"
        st.rerun()

with col2:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#059669;">
        <div class="kpi-icon">💵</div>
        <div class="kpi-label">Efectivo</div>
        <div class="kpi-value">S/ {efectivo_total:,.2f}</div>
        <div class="kpi-sub">{pct_efectivo:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_efectivo", use_container_width=True):
        st.session_state.vista_detalle = "efectivo"
        st.rerun()

with col3:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#7C3AED;">
        <div class="kpi-icon">📱</div>
        <div class="kpi-label">Digital (Caja)</div>
        <div class="kpi-value">S/ {digital_total:,.2f}</div>
        <div class="kpi-sub">{len(df_digital)} trans</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_digital", use_container_width=True):
        st.session_state.vista_detalle = "digital"
        st.rerun()

with col4:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#0891B2;">
        <div class="kpi-icon">💳</div>
        <div class="kpi-label">Izipay</div>
        <div class="kpi-value">S/ {izipay_total:,.2f}</div>
        <div class="kpi-sub">{len(df_izipay_f)} trans</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_izipay", use_container_width=True):
        st.session_state.vista_detalle = "izipay"
        st.rerun()

col5, col6, col7 = st.columns(3)
with col5:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#EC4899;">
        <div class="kpi-icon">📲</div>
        <div class="kpi-label">Yape</div>
        <div class="kpi-value">S/ {yape_total:,.2f}</div>
        <div class="kpi-sub">{len(df_yape_f)} trans</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_yape", use_container_width=True):
        st.session_state.vista_detalle = "yape"
        st.rerun()

with col6:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#F97316;">
        <div class="kpi-icon">🏦</div>
        <div class="kpi-label">BCP</div>
        <div class="kpi-value">S/ {bcp_total:,.2f}</div>
        <div class="kpi-sub">{len(df_bcp_f)} trans</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_bcp", use_container_width=True):
        st.session_state.vista_detalle = "bcp"
        st.rerun()

with col7:
    st.markdown(f"""
    <div class="kpi-container" style="border-top-color:#DC2626;">
        <div class="kpi-icon">🚨</div>
        <div class="kpi-label">Alertas</div>
        <div class="kpi-value">{total_alertas}</div>
        <div class="kpi-sub">S/ {riesgo_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔍 Ver Detalle", key="ver_alertas", use_container_width=True):
        st.session_state.vista_detalle = "alertas"
        st.rerun()

# VISTA DE DETALLE
if st.session_state.vista_detalle:
    st.markdown("---")
    detalles_config = {
        "ingreso": {"title": "💰 Detalle de Ingresos Totales", "df": df_ventas_f, "color": "#1E40AF"},
        "efectivo": {"title": "💵 Detalle de Ventas en Efectivo", 
                    "df": df_ventas_f[df_ventas_f["metodo_pago"] == "Efectivo"] if len(df_ventas_f) > 0 else pd.DataFrame(), "color": "#059669"},
        "digital": {"title": "📱 Detalle de Ventas Digitales (Caja)", "df": df_digital, "color": "#7C3AED"},
        "izipay": {"title": "💳 Detalle de Cobros Izipay", "df": df_izipay_f, "color": "#0891B2"},
        "yape": {"title": "📲 Detalle de Cobros Yape", "df": df_yape_f, "color": "#EC4899"},
        "bcp": {"title": "🏦 Detalle de Cobros BCP", "df": df_bcp_f, "color": "#F97316"},
        "alertas": {"title": "🚨 Detalle de Todas las Alertas", "df": alertas_caja, "color": "#DC2626"},
    }
    config = detalles_config[st.session_state.vista_detalle]
    df_detalle = config["df"]
    total_monto = 0
    if "monto_pagado" in df_detalle.columns:
        total_monto = df_detalle["monto_pagado"].sum()
    elif "Monto total" in df_detalle.columns:
        total_monto = df_detalle["Monto total"].sum()
    elif "Monto" in df_detalle.columns:
        total_monto = df_detalle["Monto"].sum()
    st.markdown(f"""
    <div class="detalle-header" style="background: linear-gradient(135deg, {config['color']} 0%, {config['color']}dd 100%);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
            <div>
                <h2>{config['title']}</h2>
                <p>📅 Fechas: {', '.join(fechas_sel)} | 🏪 Cajas: {', '.join(cajas_sel)}</p>
            </div>
            <div style="text-align:right;">
                <div style="font-size:32px; font-weight:800;">S/ {total_monto:,.2f}</div>
                <div style="font-size:13px; opacity:0.9;">{len(df_detalle)} transacciones</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_c1, col_c2 = st.columns([1, 5])
    with col_c1:
        if st.button("❌ Cerrar Detalle", use_container_width=True, type="secondary"):
            st.session_state.vista_detalle = None
            st.rerun()
    if len(df_detalle) > 0:
        st.dataframe(df_detalle, use_container_width=True, hide_index=True, height=400)
        csv = df_detalle.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"📥 Descargar Detalle {st.session_state.vista_detalle.upper()} (CSV)",
            csv, f"detalle_{st.session_state.vista_detalle}.csv", "text/csv"
        )
    else:
        st.info("No hay datos para mostrar")
    st.markdown("---")

# ============================================================
# QUIEBRES POR CAJA
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
        ventas_c = df_ventas_base[(df_ventas_base["caja"] == caja_info["caja"]) & 
                                    (df_ventas_base["fecha"] == caja_info["fecha"])]
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
        vh = df_izipay_f.groupby("Hora")["Monto total"].sum().reset_index().sort_values("Hora")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=vh["Hora"].astype(str), y=vh["Monto total"],
            marker=dict(color=vh["Monto total"], colorscale=[[0, "#DBEAFE"], [1, "#1E40AF"]], showscale=False),
            text=[f"S/{v:.0f}" for v in vh["Monto total"]], textposition="outside"
        ))
        fig.update_layout(title="<b>📈 Flujo de Ventas por Hora - Izipay</b>",
            xaxis_title="Hora", yaxis_title="Monto (S/)",
            plot_bgcolor="white", paper_bgcolor="white", height=400)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    metodos = df_ventas_f.groupby("metodo_pago")["monto_pagado"].sum().reset_index()
    if len(metodos) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=metodos["metodo_pago"], values=metodos["monto_pagado"], hole=0.55,
            marker=dict(colors=["#059669", "#7C3AED", "#D97706", "#0891B2"], line=dict(color="white", width=3)),
            textinfo="label+percent")])
        fig.update_layout(title="<b>🥧 Distribución por Método</b>",
            height=400, showlegend=False, paper_bgcolor="white",
            annotations=[dict(text=f"<b>S/ {ingreso_total:,.0f}</b>", x=0.5, y=0.5, font=dict(size=18), showarrow=False)])
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
    fig = go.Figure(data=[
        go.Bar(name='💳 Izipay', x=["Cobros"], y=[izipay_total], marker_color="#0891B2",
               text=[f"S/{izipay_total:.0f}"], textposition='outside'),
        go.Bar(name='📲 Yape', x=["Cobros"], y=[yape_total], marker_color="#EC4899",
               text=[f"S/{yape_total:.0f}"], textposition='outside'),
        go.Bar(name='🏦 BCP', x=["Cobros"], y=[bcp_total], marker_color="#F97316",
               text=[f"S/{bcp_total:.0f}"], textposition='outside'),
    ])
    fig.update_layout(title="<b>⚖️ Comparativo de Canales</b>", barmode='group',
                     plot_bgcolor="white", paper_bgcolor="white", height=400)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FUNCIÓN: TABLA CON JUSTIFICACIÓN Y MOTIVO (para todas las alertas)
# ============================================================
def tabla_con_justificacion(df, tipo_alerta, cols_base, key_suffix):
    """Renderiza tabla con columnas de Justificación y Motivo editables"""
    if len(df) == 0:
        return None
    
    df_display = df.copy().reset_index(drop=True)
    # Crear ID único basado en el tipo de alerta
    if tipo_alerta == "caja":
        df_display["ID"] = df_display.apply(
            lambda r: f"caja_{r['Fecha']}_{r['Caja']}_{r['Op']}_{r['Doc']}", axis=1
        )
    else:
        # Para huérfanos, usar hora + monto + tipo
        df_display["ID"] = df_display.apply(
            lambda r: f"{tipo_alerta}_{r.get('Hora_str', 'N')}_{r['Monto total']:.2f}", axis=1
        )
    
    df_display["Justificación"] = df_display["ID"].apply(
        lambda i: justificaciones.get(i, {}).get("estado", "🟡 Pendiente")
    )
    df_display["Motivo"] = df_display["ID"].apply(
        lambda i: justificaciones.get(i, {}).get("motivo", "")
    )
    
    cols_mostrar = cols_base + ["Justificación", "Motivo"]
    
    edited_df = st.data_editor(
        df_display[cols_mostrar],
        column_config={
            "Justificación": st.column_config.SelectboxColumn(
                "Justificación", width="medium",
                options=["🟡 Pendiente", "🟢 Justificado", "🔴 Fraude confirmado"],
                required=True,
            ),
            "Motivo": st.column_config.TextColumn("Motivo", width="large"),
            "Monto total": st.column_config.NumberColumn("Monto", format="S/ %.2f"),
            "Monto": st.column_config.NumberColumn("Monto", format="S/ %.2f"),
        },
        disabled=[c for c in cols_base],
        hide_index=True, use_container_width=True,
        key=f"editor_{tipo_alerta}_{key_suffix}"
    )
    
    if st.button(f"💾 Guardar Justificaciones {tipo_alerta.upper()}", 
                 type="primary", key=f"btn_save_{tipo_alerta}_{key_suffix}"):
        for idx, row in edited_df.iterrows():
            original_row = df_display.iloc[idx]
            id_alerta = original_row["ID"]
            justificaciones[id_alerta] = {
                "estado": row["Justificación"],
                "motivo": row["Motivo"],
                "fecha_registro": datetime.now().isoformat()
            }
        data["justificaciones"] = justificaciones
        guardar_historial(data)
        st.success("✅ Guardado")
        st.rerun()
    
    return edited_df

# ============================================================
# ALERTAS
# ============================================================
st.markdown('<div class="section-title">🚨 Detalle de Alertas</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    f"🚨 Caja sin Cobro ({len(alertas_caja)})",
    f"⚠️ Izipay sin Caja ({len(izipay_huerf)})",
    f"📲 Yape sin Caja ({len(yape_huerf)})",
    f"🏦 BCP sin Caja ({len(bcp_huerf)})",
    f"📋 Todas ({len(df_res)})"
])

with tab1:
    if len(alertas_caja) > 0:
        st.error(f"⚠️ **{len(alertas_caja)} ventas sospechosas** por **S/ {monto_sospechoso:.2f}**")
        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            cajas_alerta = ["Todas"] + sorted(alertas_caja["Caja"].unique().tolist())
            filtro_caja = st.selectbox("🏪 Filtrar por caja", cajas_alerta, key="filtro_caja_alerta")
        if filtro_caja != "Todas":
            df_display = alertas_caja[alertas_caja["Caja"] == filtro_caja].copy()
        else:
            df_display = alertas_caja.copy()
        df_display = df_display.reset_index(drop=True)
        df_display["ID"] = df_display.apply(
            lambda r: f"caja_{r['Fecha']}_{r['Caja']}_{r['Op']}_{r['Doc']}", axis=1
        )
        df_display["Justificación"] = df_display["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("estado", "🟡 Pendiente")
        )
        df_display["Motivo"] = df_display["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("motivo", "")
        )
        st.markdown("**✏️ Edita la Justificación y Motivo. La columna 🔗 Posible Relación te ayuda a identificar cobros huérfanos con el mismo monto.**")
        
        if "Posible Relación" in df_display.columns:
            cols_mostrar = ["Fecha", "Caja", "Op", "Doc", "Método", "Ref", "Monto", 
                           "Estado", "Posible Relación", "Justificación", "Motivo"]
        else:
            cols_mostrar = ["Fecha", "Caja", "Op", "Doc", "Método", "Ref", "Monto", 
                           "Estado", "Justificación", "Motivo"]
        
        edited_df = st.data_editor(
            df_display[cols_mostrar],
            column_config={
                "Justificación": st.column_config.SelectboxColumn(
                    "Justificación", width="medium",
                    options=["🟡 Pendiente", "🟢 Justificado", "🔴 Fraude confirmado"],
                    required=True,
                ),
                "Motivo": st.column_config.TextColumn("Motivo", width="large"),
                "Monto": st.column_config.NumberColumn("Monto", format="S/ %.2f"),
                "Posible Relación": st.column_config.TextColumn(
                    "🔗 Posible Relación", width="large",
                    help="Cobros huérfanos con el mismo monto"
                ),
            },
            disabled=["Fecha", "Caja", "Op", "Doc", "Método", "Ref", "Monto", "Estado", "Posible Relación"],
            hide_index=True, use_container_width=True,
            key=f"editor_alertas_{filtro_caja}"
        )
        col_g1, col_g2 = st.columns([1, 4])
        with col_g1:
            if st.button("💾 Guardar Justificaciones", type="primary", use_container_width=True, key="save_caja"):
                for idx, row in edited_df.iterrows():
                    original_row = df_display.iloc[idx]
                    id_alerta = original_row["ID"]
                    justificaciones[id_alerta] = {
                        "estado": row["Justificación"],
                        "motivo": row["Motivo"],
                        "fecha_registro": datetime.now().isoformat()
                    }
                data["justificaciones"] = justificaciones
                guardar_historial(data)
                st.success("✅ Guardado")
                st.rerun()
        st.markdown("---")
        col_r1, col_r2, col_r3 = st.columns(3)
        pendientes = (edited_df["Justificación"] == "🟡 Pendiente").sum()
        justificadas = (edited_df["Justificación"] == "🟢 Justificado").sum()
        fraudes = (edited_df["Justificación"] == "🔴 Fraude confirmado").sum()
        with col_r1: st.metric("🟡 Pendientes", pendientes)
        with col_r2: st.metric("🟢 Justificadas", justificadas)
        with col_r3: st.metric("🔴 Fraudes", fraudes)
    else:
        st.success("✅ No hay ventas sin cobro")

with tab2:
    if len(izipay_huerf) > 0:
        st.warning(f"⚠️ **{len(izipay_huerf)} cobros Izipay sin registrar** por **S/ {monto_no_reg_izi:.2f}**")
        tabla_con_justificacion(
            izipay_huerf, "izipay",
            ["Hora_str", "Medio de cobro", "Monto total", "Estado de venta"],
            "izi"
        )
    else:
        st.success("✅ Todos los cobros Izipay registrados")

with tab3:
    if len(yape_huerf) > 0:
        st.warning(f"⚠️ **{len(yape_huerf)} cobros Yape sin registrar** por **S/ {monto_no_reg_yape:.2f}**")
        tabla_con_justificacion(
            yape_huerf, "yape",
            ["Hora_str", "Monto total"],
            "yp"
        )
    else:
        st.success("✅ Todos los cobros Yape registrados")

with tab4:
    if len(bcp_huerf) > 0:
        st.warning(f"⚠️ **{len(bcp_huerf)} cobros BCP sin registrar** por **S/ {monto_no_reg_bcp:.2f}**")
        cols_bcp = ["Monto total"]
        if "descripcion" in bcp_huerf.columns: cols_bcp.append("descripcion")
        if "num_operacion" in bcp_huerf.columns: cols_bcp.append("num_operacion")
        tabla_con_justificacion(
            bcp_huerf, "bcp",
            cols_bcp,
            "bc"
        )
    else:
        st.success("✅ Todos los cobros BCP registrados")

with tab5:
    if len(df_res) > 0:
        df_res_display = df_res.copy().reset_index(drop=True)
        df_res_display["ID"] = df_res_display.apply(
            lambda r: f"caja_{r['Fecha']}_{r['Caja']}_{r['Op']}_{r['Doc']}", axis=1
        )
        df_res_display["Justificación"] = df_res_display["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("estado", "-")
        )
        df_res_display["Motivo"] = df_res_display["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("motivo", "")
        )
        df_res_display = df_res_display.drop(columns=["ID"])
        st.dataframe(df_res_display, use_container_width=True, hide_index=True)

# ============================================================
# DESCARGAR
# ============================================================
st.markdown('<div class="section-title">📥 Descargar Reportes</div>', unsafe_allow_html=True)

col_f, _ = st.columns([1, 3])
with col_f:
    opciones_caja = ["Todas"] + sorted(df_ventas["caja"].unique().tolist()) if len(df_ventas) > 0 else ["Todas"]
    caja_download = st.selectbox("🏪 Filtrar descarga por caja", opciones_caja, key="caja_download")

if caja_download != "Todas":
    df_ventas_dl = df_ventas_f[df_ventas_f["caja"] == caja_download] if len(df_ventas_f) > 0 else pd.DataFrame()
    alertas_dl = alertas_caja[alertas_caja["Caja"] == caja_download] if len(alertas_caja) > 0 else pd.DataFrame()
else:
    df_ventas_dl = df_ventas_f
    alertas_dl = alertas_caja

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if len(df_ventas_dl) > 0:
        csv = df_ventas_dl.to_csv(index=False).encode('utf-8')
        nombre = f"ventas_{caja_download.replace(' ', '_').lower()}.csv"
        st.download_button("📊 Ventas", csv, nombre, "text/csv", use_container_width=True)
with col2:
    if len(alertas_dl) > 0:
        alertas_export = alertas_dl.copy().reset_index(drop=True)
        alertas_export["ID"] = alertas_export.apply(
            lambda r: f"caja_{r['Fecha']}_{r['Caja']}_{r['Op']}_{r['Doc']}", axis=1
        )
        alertas_export["Justificación"] = alertas_export["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("estado", "🟡 Pendiente")
        )
        alertas_export["Motivo"] = alertas_export["ID"].apply(
            lambda i: justificaciones.get(i, {}).get("motivo", "")
        )
        alertas_export = alertas_export.drop(columns=["ID"])
        csv = alertas_export.to_csv(index=False).encode('utf-8')
        nombre = f"alertas_{caja_download.replace(' ', '_').lower()}.csv"
        st.download_button("🚨 Alertas", csv, nombre, "text/csv", use_container_width=True)
with col3:
    if len(izipay_huerf) > 0:
        csv = izipay_huerf.to_csv(index=False).encode('utf-8')
        st.download_button("⚠️ Huérf.Izi", csv, "huerf_izi.csv", "text/csv", use_container_width=True)
with col4:
    if len(yape_huerf) > 0:
        csv = yape_huerf.to_csv(index=False).encode('utf-8')
        st.download_button("📲 Huérf.Yape", csv, "huerf_yape.csv", "text/csv", use_container_width=True)
with col5:
    if len(bcp_huerf) > 0:
        csv = bcp_huerf.to_csv(index=False).encode('utf-8')
        st.download_button("🏦 Huérf.BCP", csv, "huerf_bcp.csv", "text/csv", use_container_width=True)

st.markdown("---")
st.caption("Dashboard Gerencial | Sistema Anti-Fraude 🐍")