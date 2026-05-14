import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import hashlib
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. CONFIGURACIÓN (CREADO POR IGNACIO DIAZ - 2026)
# ============================================================
SHEET_ID        = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES    = "1392659349"
GID_CARGAS      = "1267917528"
GID_VIP         = "968995524"

URL_CARGAS_POST   = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

# PIN desde secrets
try:
    ADMIN_PIN = st.secrets["ADMIN_PIN"]
except Exception:
    ADMIN_PIN = "1323"

TIEMPO_EXCLUSIVO_MIN = 30
WSP_VENTAS_VIP       = "5493406649346"
HORAS_EXPIRACION     = 72   # ocultar publicaciones con más de X horas

# Peajes aproximados entre zonas
PEAJES_REF = {
    "ROSARIO": 3500, "CORDOBA": 5200, "BAHIA BLANCA": 7800,
    "TUCUMAN": 9500, "SALTA": 12000, "SANTA FE": 2800,
    "PARANA": 3200, "CAMPANA": 6500, "ZARATE": 6200,
}

# ============================================================
# 2. BASE DE CIUDADES
# ============================================================
COORDS_CIUDADES = {
    "TODAS": (0, 0),
    "SAN JORGE (SF)": (-31.896, -61.859),   "ROSARIO (SF)": (-32.946, -60.639),
    "SANTA FE (SF)": (-31.633, -60.700),    "RAFAELA (SF)": (-31.250, -61.486),
    "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237),   "AVELLANEDA (SF)": (-29.117, -59.658),
    "CRISPI (SF)": (-31.721, -61.916),      "SASTRE (SF)": (-31.766, -61.828),
    "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
    "TIMBUES (SF)": (-32.668, -60.751),     "PTO GRAL SAN MARTIN (SF)": (-32.745, -60.732),
    "SAN LORENZO (SF)": (-32.746, -60.734),
    "CORDOBA (CBA)": (-31.413, -64.181),    "SAN FRANCISCO (CBA)": (-31.427, -62.082),
    "RIO CUARTO (CBA)": (-33.123, -64.348), "VILLA MARIA (CBA)": (-32.407, -63.240),
    "JESUS MARIA (CBA)": (-30.981, -64.093),"MARCOS JUAREZ (CBA)": (-32.697, -62.106),
    "BAHIA BLANCA (BA)": (-38.718, -62.266),"QUEQUEN (BA)": (-38.541, -58.713),
    "CAMPANA (BA)": (-34.163, -58.959),     "ZARATE (BA)": (-34.096, -59.024),
    "RAMALLO (BA)": (-33.483, -60.000),     "PERGAMINO (BA)": (-33.891, -60.573),
    "PARANA (ER)": (-31.733, -60.529),      "VICTORIA (ER)": (-32.624, -60.155),
    "SGO DEL ESTERO": (-27.795, -64.263),   "TUCUMAN": (-26.824, -65.222),
    "SALTA": (-24.785, -65.411),
}

# ============================================================
# 3. GESTIÓN DE SESIÓN
# ============================================================
defaults = {
    "admin_mode": False,
    "anuncios": "¡Bienvenido al Sistema VIP!",
    "situacion_actual": "Sin reportes de demoras por el momento.",
    "search_query": "",
    "reportes_puerto": "Normal - Sin demoras reportadas en accesos.",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# 4. CARGA DE DATOS
# ============================================================
@st.cache_data(ttl=60)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")

        if not df_ca.empty:
            mask_borrado = df_ca.iloc[:, 1].astype(str).str.contains("BORRADO", case=False)
            df_ca = df_ca[~mask_borrado]

        vips = []
        try:
            url_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
            df_v = pd.read_csv(url_vip, header=None)
            if not df_v.empty:
                vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass

        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# ============================================================
# 5. FUNCIONES AUXILIARES
# ============================================================
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    clean_num = limpiar_wsp(num)
    msg = f"Hola! Vi tu camión de {origen} a {destino} en Retorno Match. ¿Tenés carga?" if es_chofer else f"Hola! Me interesa la carga de {origen} a {destino} que publicaste en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    msg = f"Hola Ignacio! Quiero solicitar el acceso VIP para el CUIT: {cuit}"
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        if horas > 0: return f"Hace {horas}h"
        return f"Hace {(diff.seconds % 3600) // 60}m"
    except: return "Reciente"

def esta_expirada(timestamp_str, horas=HORAS_EXPIRACION):
    try:
        dt = pd.to_datetime(timestamp_str)
        return (datetime.now() - dt).total_seconds() > horas * 3600
    except: return False

def badge_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff_h = (datetime.now() - dt).total_seconds() / 3600
        texto = formatear_fecha(timestamp_str)
        color = "#e74c3c" if diff_h > 48 else ("#f39c12" if diff_h > 24 else "#8b949e")
        return f'<div class="badge-time" style="color:{color};">{texto}</div>'
    except: return '<div class="badge-time">Reciente</div>'

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0, 0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0, 0))
    if lat1 == 0 or lat2 == 0: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def estimar_peajes(destino):
    for ciudad, valor in PEAJES_REF.items():
        if ciudad in str(destino).upper(): return valor
    return 2000

def obtener_clima(ciudad):
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"
        res = requests.get(url, timeout=4).json()
        temp = res["current_weather"]["temperature"]
        return f"🌡️ {temp}°C"
    except: return "N/A"

# ============================================================
# 6. ESTILOS (TEMA DARK PROFESIONAL)
# ============================================================
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .card-cosecha { background: #1c2a1c; border: 1px solid #2d4d2d; color: #8ebf8e; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #4caf50; position: relative; }
    .card-expirada { background: #1a1a1a; color: #555; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px dashed #333; border-left: 6px solid #555; position: relative; opacity: 0.6; }
    .vip-access-box { background: #1c2128; border: 2px solid #f1c40f; padding: 20px; border-radius: 15px; margin-bottom: 25px; text-align: center; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,75,75,0.4); } 70% { box-shadow: 0 0 0 10px rgba(255,75,75,0); } 100% { box-shadow: 0 0 0 0 rgba(255,75,75,0); } }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 7. SIDEBAR ADMIN
# ============================================================
with st.sidebar:
    st.title("🛡️ Gestión")
    pin_input = st.text_input("PIN Admin", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual:", st.session_state.situacion_actual)
        st.session_state.reportes_puerto = st.text_area("🚢 Reporte Puertos:", st.session_state.reportes_puerto)
        if st.button("♻️ Forzar Sincronización"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.session_state.admin_mode = False
    st.divider()
    st.caption("Creado por Ignacio Diaz - 2026")

# ============================================================
# 8. CUERPO PRINCIPAL
# ============================================================
st.title("🚛 RETORNO MATCH VIP")

# Marquesina
st.markdown(f'<div style="background:#21262d; border:1px solid #30363d; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# Acceso VIP
with st.container():
    st.markdown('<div class="vip-access-box">', unsafe_allow_html=True)
    user_cuit = st.text_input("Ingrese su CUIT para desbloquear contactos:", placeholder="Ej: 20304445556").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL
    if user_cuit:
        if es_user_vip: st.success("✅ ACCESO VIP ACTIVO")
        else: st.error("❌ CUIT no registrado."); st.markdown(f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" style="color:#f1c40f; font-weight:bold;">👉 Solicitar acceso por WhatsApp</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

lock_btn_html = f'<div style="background:#444; color:#f1c40f; padding:10px; border-radius:8px; text-align:center; font-size:0.8rem; border:1px solid #f1c40f;">⭐ SOLO VIP</div>'

# --- TAB 1: CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if not esta_expirada(r.iloc[0]):
                btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" target="_blank" style="background:#238636; color:white; padding:10px; display:block; text-align:center; border-radius:8px; text-decoration:none;">OFERTAR</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
                st.markdown(f'<div class="card-white">{badge_fecha(r.iloc[0])}<span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br>EQ: {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}{btn}</div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains("ARRIME", case=False)]
        for _, r in df_ca_v.iterrows():
            if not esta_expirada(r.iloc[0]):
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                btn = f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" style="background:#2980b9; color:white; padding:10px; display:block; text-align:center; border-radius:8px; text-decoration:none;">SOLICITAR</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
                st.markdown(f'<div class="{estilo}">{badge_fecha(r.iloc[0])}<div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>📦 {r.iloc[3]} | 🏢 {r.iloc[5]}{btn}</div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains("ARRIME", case=False)]
        for _, r in df_arr.iterrows():
            btn = f'<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" style="background:#238636; color:white; padding:10px; display:block; text-align:center; border-radius:8px; text-decoration:none;">CONTACTAR</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
            st.markdown(f'<div class="card-cosecha">{badge_fecha(r.iloc[0])}<b>ZONA: {r.iloc[2]}</b><br>🌾 {r.iloc[3]}{btn}</div>', unsafe_allow_html=True)

# --- TAB 4: CALCULADOR DE COSTOS (CORREGIDO) ---
with tab4:
    st.subheader("📊 Estimador de Costos")
    c1, c2 = st.columns(2)
    o_c = c1.selectbox("Origen", list(COORDS_CIUDADES.keys()))
    d_c = c2.selectbox("Destino", list(COORDS_CIUDADES.keys()))
    
    t_km = st.number_input("Tarifa $/KM", value=1300)
    dist = calcular_distancia(o_c, d_c) * 1.22
    
    if dist > 0:
        total = dist * t_km
        st.metric("Distancia Aprox.", f"{dist:.0f} KM")
        st.metric("Total Sugerido", f"$ {total:,.0f}")
        
        # Tarifa por Tonelada
        st.markdown("---")
        st.markdown("### 🌾 Tarifa por Tonelada")
        col_ton, col_res = st.columns(2)
        ton = col_ton.number_input("Toneladas", value=30)
        t_ton = total / ton if ton > 0 else 0
        col_res.metric("$/Tonelada", f"$ {t_ton:,.2f}")
    else:
        st.info("Seleccione ciudades para calcular.")

# Pie de página
st.markdown("---")
st.markdown('<div style="text-align:center; color:#555; font-size:0.8rem;">Creado por Ignacio Diaz | © 2026</div>', unsafe_allow_html=True)
