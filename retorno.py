import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
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
WSP_VENTAS_VIP = "5493401525621"

COORDS_CIUDADES = {
    "TODAS": (0,0), "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639),
    "SANTA FE (SF)": (-31.633, -60.700), "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395),
    "VENADO TUERTO (SF)": (-33.745, -61.968), "PERGAMINO (BA)": (-33.891, -60.573), "SGO DEL ESTERO": (-27.795, -64.263)
}

# --- 2. GESTIÓN DE SESIÓN ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "estado_puertos" not in st.session_state: st.session_state.estado_puertos = "🚢 PUERTOS: Operativos"
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "modo_ruta" not in st.session_state: st.session_state.modo_ruta = False

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except: return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return "549" + (clean[1:] if clean.startswith("0") else clean).replace("15", "", 1) if clean else "5491111111111"

def generar_wsp_link(num, o, d, es_ch=True):
    msg = f"Hola! Vi tu {'camión' if es_ch else 'carga'} de {o} a {d} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={limpiar_wsp(num)}&text={urllib.parse.quote(msg)}"

def link_maps(o, d): return f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(o)}&destination={urllib.parse.quote(d)}"

def formatear_fecha(ts):
    try:
        dt = pd.to_datetime(ts)
        diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        return f"Hace {diff.seconds // 3600}h" if diff.seconds // 3600 > 0 else f"Hace {diff.seconds // 60}m"
    except: return "Reciente"

def calcular_distancia(o, d):
    l1, ln1 = COORDS_CIUDADES.get(o, (0,0))
    l2, ln2 = COORDS_CIUDADES.get(d, (0,0))
    if l1 == 0 or l2 == 0: return 0
    a = math.sin(math.radians(l2-l1)/2)**2 + math.cos(math.radians(l1))*math.cos(math.radians(l2))*math.sin(math.radians(ln2-ln1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# CSS INYECTADO SIN INDENTACIÓN (CRÍTICO)
st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #adbac7; }
.card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
.card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; border-left: 6px solid #ff4b4b; position: relative; }
.badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }
.route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
.btn-wsp { background: #238636; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; flex: 2; }
.btn-maps { background: #30363d; color: #adbac7 !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; border: 1px solid #444; flex: 1; }
.container-btns { display: flex; gap: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & HEADER ---
with st.sidebar:
    st.title("🛡️ Panel Control")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("Anuncio:", st.session_state.anuncios)
        st.session_state.estado_puertos = st.text_input("Puertos:", st.session_state.estado_puertos)
    st.session_state.modo_ruta = st.toggle("🚚 MODO RUTA", value=st.session_state.modo_ruta)

st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios} -- CREADO POR IGNACIO DIAZ</b></marquee></div>', unsafe_allow_html=True)
st.info(st.session_state.estado_puertos)

busqueda = st.text_input("🔎 BUSCAR CIUDAD:", value=st.session_state.search_query).upper()
t1, t2, t3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "📊 COSTOS"])

# --- TAB 2: CARGAS (CORRECCIÓN DE RENDERIZADO) ---
with t2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if busqueda in str(r).upper():
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                # RENDERIZADO DIRECTO SIN ESPACIOS
                st.markdown(f"""<div class="{estilo}">
<div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
<div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
📦 {r.iloc[3]} | 🏢 {r.iloc[5]}
<div class="container-btns">
<a href="{link_maps(r.iloc[1], r.iloc[2])}" class="btn-maps" target="_blank">🗺️ Mapa</a>
<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" class="btn-wsp" target="_blank">PEDIR VIAJE</a>
</div>
</div>""", unsafe_allow_html=True)

# --- TAB 3: COSTOS ---
with t3:
    o_c = st.selectbox("Origen", list(COORDS_CIUDADES.keys()))
    d_c = st.selectbox("Destino", list(COORDS_CIUDADES.keys()))
    dist = calcular_distancia(o_c, d_c)
    if dist > 0:
        st.metric("Distancia Estimada", f"{(dist * 1.25):.0f} KM")

st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
