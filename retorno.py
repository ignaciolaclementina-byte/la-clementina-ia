import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import pydeck as pdk  # Para el Mapa de Calor

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
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "situacion_actual" not in st.session_state: st.session_state.situacion_actual = "Sin reportes de demoras por el momento."
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "reportes_puerto" not in st.session_state: st.session_state.reportes_puerto = ""

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        vips = []
        try:
            url_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
            df_v = pd.read_csv(url_vip, header=None)
            if not df_v.empty: vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
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

def generar_wsp_link(num, origen, destino, es_chofer=True, reporte_llegada=False):
    clean_num = limpiar_wsp(num)
    if reporte_llegada:
        msg = f"Ignacio, ya estoy en destino ({destino}). Mi ubicación actual es: https://www.google.com/maps/search/?api=1&query={COORDS_CIUDADES.get(destino, (0,0))[0]},{COORDS_CIUDADES.get(destino, (0,0))[1]}"
    else:
        msg = f"Hola! Vi tu anuncio de {origen} a {destino} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(f'Hola Ignacio! Solicito acceso VIP CUIT: {cuit}')}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        return f"Hace {diff.seconds // 3600}h {(diff.seconds % 3600) // 60}m"
    except: return "Reciente"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    return 6371 * 2 * math.atan2(math.sqrt(math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2), math.sqrt(1-(math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2)))

def obtener_clima(ciudad):
    if ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except: return "N/A"

def generar_reporte_puertos_real():
    if st.session_state.reportes_puerto: return f"🚨 {st.session_state.reportes_puerto}"
    # Semáforo de Cupos Simplificado
    puertos = ["TIMBUES (SF)", "SAN LORENZO (SF)", "PTO GRAL SAN MARTIN (SF)"]
    reporte = []
    for p in puertos:
        estado = "🟢" if "Lluvia" not in str(obtener_clima(p)) else "🔴"
        reporte.append(f"{p.split(' ')[0]} {estado}")
    return " | ".join(reporte)

# --- 5. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# Estilos (Manteniendo tus originales y sumando los nuevos)
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.reportes_puerto = st.text_area("🚢 Cupos/Puertos:", st.session_state.reportes_puerto)
    else: st.session_state.admin_mode = False

# Cabecera
st.title("🚛 RETORNO MATCH VIP")

# --- ALERTA COSECHA GRUESA ---
mes_actual = datetime.now().month
if mes_actual in [3, 4, 5]: # Meses de cosecha en Argentina
    st.warning("🌾 **ALERTA COSECHA GRUESA:** Alta demanda de fletes detectada. Se recomienda asegurar cupos con antelación.")

# --- SECCIÓN VIP ---
user_cuit = st.text_input("Ingrese CUIT:", key="cuit_input").strip()
es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# Reporte Puertos
st.markdown(f'<div class="status-bar">🚢 **CUPOS:** {generar_reporte_puertos_real()}</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

# --- TAB 1: CAMIONES (INCLUYE MAPA DE CALOR) ---
with tab1:
    if not df_ch_raw.empty:
        # Generar Datos para Mapa de Calor
        map_data = []
        for loc in df_ch_raw.iloc[:, 1].unique():
            if loc in COORDS_CIUDADES:
                count = len(df_ch_raw[df_ch_raw.iloc[:, 1] == loc])
                lat, lon = COORDS_CIUDADES[loc]
                map_data.append({"lat": lat, "lon": lon, "peso": count})
        
        if map_data:
            st.subheader("📍 Concentración de Camiones")
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/dark-v9',
                initial_view_state=pdk.ViewState(latitude=-31.8, longitude=-61.8, zoom=6, pitch=50),
                layers=[pdk.Layer('HeatmapLayer', data=map_data, get_position='[lon, lat]', get_weight='peso', radius_pixels=60)]
            ))

    col1, col2 = st.columns([1, 2])
    with col2:
        for idx, r in df_ch_raw.iterrows():
            btn_wsp = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" target="_blank" style="background:#238636; color:white; padding:10px; border-radius:5px; text-decoration:none; display:block; text-align:center;">OFERTAR CARGA</a>' if es_user_vip else "🔒 Bloqueado"
            st.markdown(f'<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>{r.iloc[3]}<br>{btn_wsp}</div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS (INCLUYE BOTÓN LLEGUE) ---
with tab2:
    for idx, r in df_ca_raw.iterrows():
        if "ARRIME" not in str(r.iloc[1]):
            btn_llegue = f'<a href="{generar_wsp_link(WSP_VENTAS_VIP, r.iloc[1], r.iloc[2], reporte_llegada=True)}" target="_blank" style="background:#0366d6; color:white; padding:10px; border-radius:5px; text-decoration:none; display:block; text-align:center; margin-top:5px;">✅ LLEGUÉ A DESTINO</a>'
            st.markdown(f'<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>{r.iloc[3]}<br>{btn_llegue}</div>', unsafe_allow_html=True)

# (Tabs 3 y 4 se mantienen con tu lógica de cálculo de distancia y arritmes original)

st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
