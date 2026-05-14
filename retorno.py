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
# 1. CONFIGURACIÓN (CREADO POR IGNACIO DIAZ)
# ============================================================
# Blindaje de autoría según requerimiento
CREADOR = "Ignacio Diaz" 

SHEET_ID        = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES    = "1392659349"
GID_CARGAS      = "1267917528"
GID_VIP         = "968995524"

URL_CARGAS_POST   = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

try:
    ADMIN_PIN = st.secrets["ADMIN_PIN"]
except Exception:
    ADMIN_PIN = "1323"

TIEMPO_EXCLUSIVO_MIN = 30
WSP_VENTAS_VIP       = "5493406649346"
HORAS_EXPIRACION     = 72   

PEAJES_REF = {
    "ROSARIO": 3500, "CORDOBA": 5200, "BAHIA BLANCA": 7800,
    "TUCUMAN": 9500, "SALTA": 12000, "SANTA FE": 2800,
    "PARANA": 3200, "CAMPANA": 6500, "ZARATE": 6200,
}

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
# 4. FUNCIONES DE MENSAJERÍA MEJORADA
# ============================================================
def generar_wsp_link(num, origen, destino, es_chofer=True):
    """Genera un mensaje de WhatsApp profesional y directo."""
    clean_num = limpiar_wsp(num)
    ahora = datetime.now().strftime("%H:%M")
    
    if es_chofer:
        msg = (
            f"Hola! Me contacto por tu camión publicado en *Retorno Match* ({ahora}hs).\n\n"
            f"📍 *Origen:* {origen}\n"
            f"🏁 *Destino:* {destino}\n"
            f"¿Todavía tenés disponibilidad? Tengo una carga para ofrecerte."
        )
    else:
        msg = (
            f"Hola! Me interesa la carga que publicaste en *Retorno Match* ({ahora}hs).\n\n"
            f"📦 *Ruta:* {origen} ➔ {destino}\n"
            f"¿Sigue disponible el viaje? Consulto por disponibilidad de equipo."
        )
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    """Mensaje mejorado para solicitud de acceso VIP."""
    msg = (
        f"Hola {CREADOR}! Solicito formalmente el acceso *VIP* para la plataforma.\n\n"
        f"🆔 *CUIT:* {cuit}\n"
        f"Quedo a la espera de la habilitación. Saludos!"
    )
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg)}"

# ============================================================
# 5. CARGA Y PROCESAMIENTO
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
            df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}", header=None)
            if not df_v.empty:
                vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass
        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

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
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    if ciudad not in COORDS_CIUDADES or ciudad == "TODAS": return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True", timeout=4).json()
        temp = res["current_weather"]["temperature"]
        return f"🌡️ {temp}°C"
    except: return "N/A"

# ============================================================
# 6. ESTILOS Y SIDEBAR
# ============================================================
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .vip-access-box { background: #1c2128; border: 2px solid #f1c40f; padding: 20px; border-radius: 15px; text-align: center; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255,75,75,0.4); } 70% { box-shadow: 0 0 0 10px rgba(255,75,75,0); } 100% { box-shadow: 0 0 0 0 rgba(255,75,75,0); } }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ Gestión")
    pin = st.text_input("PIN Admin", type="password")
    if pin == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.reportes_puerto = st.text_area("🚢 Reporte Puertos:", st.session_state.reportes_puerto)
    else: st.session_state.admin_mode = False

    st.divider()
    st.caption(f"Creado por {CREADOR} - 2026") #
    st.caption(f"🕐 {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# 7. INTERFAZ PRINCIPAL
# ============================================================
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# Sección VIP
with st.container():
    st.markdown('<div class="vip-access-box">', unsafe_allow_html=True)
    st.subheader("🔑 ACCESO VIP")
    user_cuit = st.text_input("CUIT para desbloquear contactos:", placeholder="Ej: 20304445556", label_visibility="collapsed").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

    if user_cuit:
        if es_user_vip:
            st.success("✅ ACCESO VIP ACTIVO")
        else:
            st.error("❌ CUIT no registrado")
            st.markdown(f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" style="color:#f1c40f; font-weight:bold;">👉 Solicitar acceso a {CREADOR} por WhatsApp</a>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ... (Resto de la lógica de Tabs y Filtros igual a la base original, pero usando las funciones mejoradas)
