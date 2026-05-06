import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime
import pytz

# --- CONFIGURACIÓN DE IDENTIDAD (IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

st.set_page_config(page_title="Retorno Match - Ignacio Diaz", page_icon="🚛", layout="wide")

# --- DISEÑO DE INTERFAZ EXCLUSIVA ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0b0e14; }
    
    .stApp { background: #0b0e14; }
    
    /* Dashboard Metrics */
    .metric-card {
        background: #161b22; border: 1px solid #30363d; border-radius: 12px;
        padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Logística Card Premium */
    .log-card {
        background: #161b22; border-radius: 12px; border-left: 6px solid #f1c40f;
        padding: 24px; margin-bottom: 20px; border-top: 1px solid #30363d;
        border-right: 1px solid #30363d; border-bottom: 1px solid #30363d;
        transition: all 0.3s ease;
    }
    .log-card:hover { transform: scale(1.01); border-left-width: 10px; background: #1c2128; }
    
    .status-new { background: #238636; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 900; }
    .route-text { font-size: 26px; font-weight: 900; color: #f0f6fc; margin: 10px 0; letter-spacing: -0.5px; }
    .data-label { color: #8b949e; font-size: 14px; text-transform: uppercase; font-weight: 700; }
    .data-value { color: #f1c40f; font-size: 18px; font-weight: 600; }
    
    /* Botón Acción */
    .btn-action {
        display: block; width: 100%; background: #f1c40f; color: #000 !important;
        text-align: center; padding: 14px; border-radius: 8px; font-weight: 800;
        text-decoration: none; margin-top: 20px; font-size: 16px;
    }
    .btn-action:hover { background: #d4ac0d; }

    /* Footer */
    .footer { text-align: center; padding: 40px; border-top: 1px solid #30363d; margin-top: 50px; }
    .creator { color: #f1c40f; font-weight: 900; font-size: 18px; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE ALTA EFICIENCIA ---
@st.cache_data(ttl=15)
def get_logistics_data():
    try:
        t = int(time.time())
        u_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        u_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
        return pd.read_csv(u_ca).fillna("-"), pd.read_csv(u_ch).fillna("-")
    except: return pd.DataFrame(), pd.DataFrame()

def format_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return ""
    return "549" + clean[-10:] if not clean.startswith("549") else clean

def time_ago(ts):
    try:
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        dt = datetime.strptime(str(ts), "%d/%m/%Y %H:%M:%S").replace(tzinfo=tz)
        diff = datetime.now(tz) - dt
        mins = int(diff.total_seconds() / 60)
        return f"Hace {mins} min" if mins < 60 else f"Hace {int(mins/60)} hs", mins < 30
    except: return "Reciente", False

# --- UI PRINCIPAL ---
st.markdown("<h1>🚛 RETORNO MATCH <span style='color:#f1c40f'>VIP</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; font-size:1.2rem;'>Centro de Gestión Logística - Ignacio Diaz</p>", unsafe_allow_html=True)

df_c, df_h = get_logistics_data()

# Stats Bar
m1, m2, m3 = st.columns(3)
with m1: st.markdown(f'<div class="metric-card"><div class="data-label">Cargas Hoy</div><div style="font-size:32px; font-weight:900;">{len(df_c)}</div></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card"><div class="data-label">Camiones</div><div style="font-size:32px; font-weight:900;">{len(df_h)}</div></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-card"><div class="data-label">Status</div><div style="color:#238636; font-size:32px; font-weight:900;">LIVE</div></div>', unsafe_allow_html=True)

# Filtros Inteligentes
st.markdown("### 🔎 Filtrar Operación")
c1, c2 = st.columns(2)
with c1: f_origen = st.text_input("📍 Punto de Carga", "").upper()
with c2: f_equipo = st.multiselect("🚛 Tipo de Unidad", ["Sider", "Batea", "Chasis", "Acoplado", "Semi"])

t1, t2 = st.tabs(["🔥 CARGAS DISPONIBLES", "🚚 RADAR DE CHOFERES"])

with t1:
    if df_c.empty: st.warning("Esperando nuevas cargas...")
    else:
        for i, row in df_c.iloc[::-1].iterrows(): # Lo último primero
            if f_origen and f_origen not in str(row.iloc[1]).upper(): continue
            
            tiempo, es_nuevo = time_ago(row.iloc[0])
            wsp = format_wsp(row.iloc[4])
            msg = urllib.parse.quote(f"Hola! Me interesa la carga de {row.iloc[3]} desde {row.iloc[1]} a {row.iloc[2]}. Sigue disponible?")
            
            st.markdown(f"""
            <div class="log-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="badge-disponible">CARGA DISPONIBLE</span>
                    <span class="status-new" style="display:{'inline' if es_nuevo else 'none'}">NUEVA</span>
                    <span style="color:#8b949e; font-size:12px;">{tiempo}</span>
                </div>
                <div class="route-text">{row.iloc[1]} ➔ {row.iloc[2]}</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                    <div><span class="data-label">Producto:</span><br><span class="data-value">{row.iloc[3]}</span></div>
                    <div><span class="data-label">Empresa:</span><br><span class="data-value">{row.iloc[5] if len(row)>5 else 'Directo'}</span></div>
                </div>
                <a href="https://wa.me/{wsp}?text={msg}" target="_blank" class="btn-action">SOLICITAR CARGA</a>
            </div>
            """, unsafe_allow_html=True)

with t2:
    if df_h.empty: st.warning("No hay camiones en radar...")
    else:
        for i, row in df_h.iloc[::-1].iterrows():
            if f_origen and f_origen not in str(row.iloc[1]).upper(): continue
            if f_equipo and str(row.iloc[3]).title() not in f_equipo: continue
            
            tiempo, _ = time_ago(row.iloc[0])
            wsp = format_wsp(row.iloc[5] if len(row)>5 else row.iloc[4])
            msg = urllib.parse.quote(f"Hola! Tengo una carga para tu unidad {row.iloc[3]} que está en {row.iloc[1]}. Te interesa?")
            
            st.markdown(f"""
            <div class="log-card" style="border-left-color: #3498db;">
                <span class="badge-disponible" style="background:#3498db; color:white;">CHOFER LIBRE</span>
                <span style="color:#8b949e; font-size:12px; float:right;">{tiempo}</span>
                <div class="route-text">{row.iloc[1]} ➔ {row.iloc[2]}</div>
                <div><span class="data-label">Equipo:</span> <span class="data-value">{row.iloc[3]}</span></div>
                <a href="https://wa.me/{wsp}?text={msg}" target="_blank" class="btn-action" style="background:#3498db; color:white !important;">ASIGNAR VIAJE</a>
            </div>
            """, unsafe_allow_html=True)

# --- FOOTER AUTORÍA (BLINDADO) ---
st.markdown(f"""
<div class="footer">
    <p style="color:#8b949e; margin-bottom:0;">Desarrollado bajo estándares VIP para</p>
    <p class="creator">IGNACIO DIAZ</p>
    <p style="color:#30363d; font-size:10px;">Versión 2026.5.1 - Estructura Nacho Blindada</p>
</div>
""", unsafe_allow_html=True)
