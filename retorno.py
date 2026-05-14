import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import folium
from streamlit_folium import folium_static

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
WSP_VENTAS_VIP = "5493406649346"

# --- BASE DE DATOS DE PUEBLOS Y CIUDADES ---
COORDS_CIUDADES = {
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "TIMBUES (SF)": (-32.668, -60.751), "PTO GRAL SAN MARTIN (SF)": (-32.745, -60.732), "SAN LORENZO (SF)": (-32.746, -60.734),
    "CORDOBA (CBA)": (-31.413, -64.181), "SAN FRANCISCO (CBA)": (-31.427, -62.082), "RIO CUARTO (CBA)": (-33.123, -64.348),
    "BAHIA BLANCA (BA)": (-38.718, -62.266), "QUEQUEN (BA)": (-38.541, -58.713), "SGO DEL ESTERO": (-27.795, -64.263)
}

# --- ESTADO DE CUPOS (Simulado/Admin) ---
if "cupos_estado" not in st.session_state:
    st.session_state.cupos_estado = {"TIMBUES": "DISPONIBLE", "SAN LORENZO": "DEMORADO", "QUEQUEN": "CERRADO"}

# --- 2. GESTIÓN DE SESIÓN Y DATOS ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"

@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        vips = []
        try:
            df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}", header=None)
            vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass
        return df_ch, df_ca, vips
    except: return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 3. FUNCIONES LÓGICA DE NEGOCIO ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return "549" + clean[-10:] if len(clean) >= 10 else "5491111111111"

def generar_wsp_llegue(patente, planta):
    msg = f"Ignacio, el camión patente {patente} ya se encuentra en zona de descarga en {planta}."
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg)}"

def obtener_clima_agro(ciudad):
    try:
        lat, lon = COORDS_CIUDADES.get(ciudad, (-31.8, -61.8))
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        return res['current_weather']['temperature'], res['current_weather']['weathercode']
    except: return 20, 0

# --- 4. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH - IGNACIO DIAZ", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 10px; border: 1px solid #30363d; border-left: 5px solid #3498db; }
    .badge-cupo { padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 0.8rem; }
    .cupo-verde { background: #238636; color: white; }
    .cupo-amarillo { background: #d29922; color: black; }
    .cupo-rojo { background: #da3633; color: white; }
</style>
""", unsafe_allow_html=True)

# SIDEBAR ADMIN
with st.sidebar:
    st.header("🛡️ Panel de Control")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("Anuncio:", st.session_state.anuncios)
        st.write("---")
        st.subheader("Gestión de Cupos")
        for planta in st.session_state.cupos_estado:
            st.session_state.cupos_estado[planta] = st.selectbox(f"Cupo {planta}", ["DISPONIBLE", "DEMORADO", "CERRADO"], index=["DISPONIBLE", "DEMORADO", "CERRADO"].index(st.session_state.cupos_estado[planta]))

# CABECERA
st.title("🚛 RETORNO MATCH")
st.info(f"📢 {st.session_state.anuncios}")

# PUNTO 1: SEMÁFORO DE CUPOS
st.subheader("🚢 Estado de Puertos & Cupos")
cols_cupos = st.columns(len(st.session_state.cupos_estado))
for i, (planta, estado) in enumerate(st.session_state.cupos_estado.items()):
    clase = "cupo-verde" if estado == "DISPONIBLE" else "cupo-amarillo" if estado == "DEMORADO" else "cupo-rojo"
    cols_cupos[i].markdown(f"<div style='text-align:center;'><b>{planta}</b><br><span class='badge-cupo {clase}'>{estado}</span></div>", unsafe_allow_html=True)

# PUNTO 2: ALERTA COSECHA (Basado en Clima)
temp, code = obtener_clima_agro("SAN JORGE (SF)")
riesgo_lluvia = code > 50
st.warning(f"🌾 **ALERTA COSECHA GRUESA:** {'⚠️ Lluvias próximas: Operativa lenta en zona San Jorge.' if riesgo_lluvia else '☀️ Clima óptimo para trilla: Alta demanda de fletes prevista.'} (Temp: {temp}°C)")

# TABS PRINCIPALES
tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES & MAPA", "🏢 CARGAS DISPONIBLES", "📍 LLEGADA A DESCARGA"])

with tab1:
    # PUNTO 4: MAPA DE CALOR/OFERTA
    st.subheader("📍 Mapa de Oferta de Camiones")
    m = folium.Map(location=[-32.5, -61.5], zoom_start=6, tiles="cartodbpositron")
    for ciudad, coords in COORDS_CIUDADES.items():
        count = len(df_ch_raw[df_ch_raw.iloc[:, 1].str.contains(ciudad, na=False)])
        if count > 0:
            folium.CircleMarker(location=coords, radius=5 + (count * 3), color="#3498db", fill=True, popup=f"{ciudad}: {count} camiones").add_to(m)
    folium_static(m)

    # Listado de Camiones
    for idx, r in df_ch_raw.iterrows():
        st.markdown(f"<div class='card-white'><b>{r.iloc[1]} ➔ {r.iloc[2]}</b><br>Equipo: {r.iloc[3]}</div>", unsafe_allow_html=True)

with tab2:
    for idx, r in df_ca_raw.iterrows():
        st.markdown(f"<div class='card-white' style='border-left-color: #f1c40f;'><b>🏢 {r.iloc[1]} ➔ {r.iloc[2]}</b><br>Carga: {r.iloc[3]}</div>", unsafe_allow_html=True)

with tab3:
    # PUNTO 3: BOTÓN DE LLEGADA
    st.subheader("🚩 Reportar Llegada a Descarga")
    with st.form("llegada"):
        pat = st.text_input("Patente del Camión").upper()
        dest = st.selectbox("Planta de Descarga", list(st.session_state.cupos_estado.keys()))
        if st.form_submit_button("ENVIAR AVISO A IGNACIO"):
            if pat:
                link = generar_wsp_llegue(pat, dest)
                st.markdown(f'<a href="{link}" target="_blank" style="background:#238636; color:white; padding:10px; border-radius:8px; text-decoration:none;">CONFIRMAR EN WHATSAPP</a>', unsafe_allow_html=True)
            else: st.error("Por favor, ingrese la patente.")

# FOOTER
st.markdown("<br><hr><center><b>Creado por Ignacio Diaz - 2026</b></center>", unsafe_allow_html=True)
