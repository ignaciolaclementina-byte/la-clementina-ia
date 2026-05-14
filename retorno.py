import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30  
WSP_VENTAS_VIP = "5493406649346"

# --- BASE DE DATOS DE PUEBLOS Y CIUDADES ---
COORDS_CIUDADES = {
    "TODAS": (0,0),
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237), "AVELLANEDA (SF)": (-29.117, -59.658), "CRISPI (SF)": (-31.721, -61.916),
    "SASTRE (SF)": (-31.766, -61.828), "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
    "TIMBUES (SF)": (-32.668, -60.751), "PTO GRAL SAN MARTIN (SF)": (-32.745, -60.732), "SAN LORENZO (SF)": (-32.746, -60.734),
    "CORDOBA (CBA)": (-31.413, -64.181), "SAN FRANCISCO (CBA)": (-31.427, -62.082), "RIO CUARTO (CBA)": (-33.123, -64.348),
    "VILLA MARIA (CBA)": (-32.407, -63.240), "JESUS MARIA (CBA)": (-30.981, -64.093), "MARCOS JUAREZ (CBA)": (-32.697, -62.106),
    "BAHIA BLANCA (BA)": (-38.718, -62.266), "QUEQUEN (BA)": (-38.541, -58.713), "CAMPANA (BA)": (-34.163, -58.959),
    "ZARATE (BA)": (-34.096, -59.024), "RAMALLO (BA)": (-33.483, -60.000), "PERGAMINO (BA)": (-33.891, -60.573),
    "PARANA (ER)": (-31.733, -60.529), "VICTORIA (ER)": (-32.624, -60.155), "SGO DEL ESTERO": (-27.795, -64.263),
    "TUCUMAN": (-26.824, -65.222), "SALTA": (-24.785, -65.411)
}

# --- 2. GESTIÓN DE SESIÓN ---
for key, val in {"admin_mode": False, "anuncios": "¡Bienvenido al Sistema VIP!", "situacion_actual": "Sin reportes de demoras.", "search_query": "", "reportes_puerto": "Normal"}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. CARGA Y LIMPIEZA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de seguridad para registros borrados
        if not df_ca.empty:
            mask_borrado = df_ca.iloc[:, 1].astype(str).str.contains('BORRADO', case=False)
            df_ca = df_ca[~mask_borrado]

        vips = []
        try:
            url_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
            df_v = pd.read_csv(url_vip, header=None)
            vips = [str(x).strip().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass
        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    msg = f"Hola! Vi tu {'camión' if es_chofer else 'carga'} de {origen} a {destino} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={limpiar_wsp(num)}&text={urllib.parse.quote(msg)}"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if 0 in [lat1, lat2]: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    if ciudad not in COORDS_CIUDADES or ciudad == "TODAS": return "N/A"
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except: return "N/A"

# --- 5. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; border-left: 6px solid #ff4b4b; position: relative; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; }
    .status-bar { background: #161b22; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR ADMIN
with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual:", st.session_state.situacion_actual)
        if st.button("♻️ Sincronizar"): st.cache_data.clear(); st.rerun()

# CABECERA
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; padding:10px; border-radius:10px; text-align:center; border: 1px solid #30363d;"><marquee style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# ACCESO VIP
with st.container():
    st.markdown('<div style="background: #1c2128; border: 2px solid #f1c40f; padding: 20px; border-radius: 15px; text-align: center; margin: 20px 0;">', unsafe_allow_html=True)
    user_cuit = st.text_input("Ingrese CUIT para ver contactos:", placeholder="Ej: 20304445556").strip()
    es_vip = user_cuit in LISTA_VIPS_GLOBAL
    if user_cuit and not es_vip:
        st.markdown(f'<a href="https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text=Solicito VIP CUIT {user_cuit}" target="_blank" style="color:#f1c40f; font-weight:bold;">👉 Solicitar Acceso VIP</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# DASHBOARD OPERATIVO
col_sit, col_clima = st.columns([3, 1])
col_sit.markdown(f'<div class="status-bar">⚠️ <b>ESTADO:</b> {st.session_state.situacion_actual}</div>', unsafe_allow_html=True)
col_clima.markdown(f'<div class="status-bar" style="border-left-color:#3498db; text-align:center;">{obtener_clima("SAN JORGE (SF)")}</div>', unsafe_allow_html=True)

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

with tab1: # CAMIONES
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" target="_blank" style="background: #238636; color: white; padding: 8px; border-radius: 5px; text-decoration: none; display: block; text-align: center; margin-top: 10px;">OFERTAR CARGA</a>' if es_vip or st.session_state.admin_mode else ""
            st.markdown(f'<div class="card-white"><span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br><b>EQ:</b> {r.iloc[3]}{btn}</div>', unsafe_allow_html=True)

with tab4: # CALCULADOR
    st.subheader("📊 Estimador de Flete")
    o = st.selectbox("Origen", list(COORDS_CIUDADES.keys()))
    d = st.selectbox("Destino", list(COORDS_CIUDADES.keys()))
    t_km = st.number_input("Tarifa $/KM", value=1350)
    dist = calcular_distancia(o, d)
    if dist > 0:
        real_km = dist * 1.22
        st.metric("Distancia Estimada", f"{real_km:.0f} KM")
        st.success(f"Sugerido: ${real_km * t_km:,.0f}")

# FOOTER
st.markdown(f"<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - {datetime.now().year}</b></div>", unsafe_allow_html=True)
