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
TIEMPO_EXCLUSIVO_MIN = 30  
WSP_VENTAS_VIP = "5493406649346"

# --- BASE DE DATOS DE PUEBLOS Y CIUDADES ---
COORDS_CIUDADES = {
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "TIMBUES (SF)": (-32.668, -60.751), "PTO GRAL SAN MARTIN (SF)": (-32.745, -60.732), "SAN LORENZO (SF)": (-32.746, -60.734),
    "CORDOBA (CBA)": (-31.413, -64.181), "SAN FRANCISCO (CBA)": (-31.427, -62.082), "RIO CUARTO (CBA)": (-33.123, -64.348),
    "BAHIA BLANCA (BA)": (-38.718, -62.266), "QUEQUEN (BA)": (-38.541, -58.713), "SGO DEL ESTERO": (-27.795, -64.263)
}

# --- 2. GESTIÓN DE SESIÓN ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "situacion_actual" not in st.session_state: st.session_state.situacion_actual = "Sin reportes de demoras."
if "search_query" not in st.session_state: st.session_state.search_query = ""
# Estado de Cupos (Controlable por Admin)
if "cupos" not in st.session_state:
    st.session_state.cupos = {"TIMBUES": "DISPONIBLE", "S. LORENZO": "DEMORADO", "QUEQUEN": "CERRADO"}

# --- 3. CARGA DE DATOS ---
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

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return "549" + clean[-10:] if len(clean) >= 10 else "5491111111111"

def generar_wsp_link(num, origen, destino, es_chofer=True):
    msg = f"Hola! Vi tu camión de {origen} a {destino} en Retorno Match. ¿Tenés carga?" if es_chofer else f"Hola! Me interesa la carga de {origen} a {destino} que publicaste."
    return f"https://api.whatsapp.com/send?phone={limpiar_wsp(num)}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        diff = datetime.now() - pd.to_datetime(timestamp_str)
        if diff.days > 0: return f"Hace {diff.days}d"
        return f"Hace {diff.seconds // 3600}h" if diff.seconds // 3600 > 0 else f"Hace {diff.seconds // 60}m"
    except: return "Reciente"

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    .cupo-box { padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Mensaje:", st.session_state.anuncios)
        st.subheader("Control de Cupos")
        for p in st.session_state.cupos:
            st.session_state.cupos[p] = st.selectbox(f"Estado {p}", ["DISPONIBLE", "DEMORADO", "CERRADO"], key=f"c_{p}")

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; padding:10px; border-radius:10px; text-align:center; border: 1px solid #30363d;"><marquee style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# --- SEMÁFORO DE CUPOS ---
st.write("")
c_cupos = st.columns(len(st.session_state.cupos))
for i, (p, est) in enumerate(st.session_state.cupos.items()):
    color = "#238636" if est == "DISPONIBLE" else "#d29922" if est == "DEMORADO" else "#da3633"
    c_cupos[i].markdown(f"<div style='text-align:center; background:#161b22; padding:10px; border-radius:8px; border-top: 4px solid {color};'><small>{p}</small><br><span style='color:{color}; font-weight:bold;'>{est}</span></div>", unsafe_allow_html=True)

# --- ACCESO VIP ---
st.write("")
with st.container():
    st.subheader("🔑 ACCESO VIP")
    user_cuit = st.text_input("Ingrese CUIT:", placeholder="Ej: 20304445556", label_visibility="collapsed").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL or st.session_state.admin_mode

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🗺️ MAPA", "🚩 LLEGADA"])

lock_btn = f'<div style="border: 1px solid #f1c40f; padding: 10px; border-radius: 8px; text-align: center; color: #f1c40f; font-size: 0.8rem;">⭐ SOLICITAR ACCESO VIP</div>'

# --- TAB 1: CAMIONES ---
with tab1:
    busqueda = st.text_input("🔎 BUSCAR (Localidad, Equipo...):").upper()
    for idx, r in df_ch_raw.iterrows():
        if busqueda in str(r).upper():
            btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" target="_blank" style="background: #238636; color: white; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px;">OFERTAR CARGA</a>' if es_user_vip else lock_btn
            st.markdown(f"""<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br><b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}{btn}</div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    for idx, r in df_ca_raw.iterrows():
        estilo = "border-left: 6px solid #ff4b4b;" if "URGENTE" in str(r.iloc[3]).upper() else ""
        btn_ca = f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" style="background: #2980b9; color: white; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px;">SOLICITAR VIAJE</a>' if es_user_vip else lock_btn
        st.markdown(f"""<div class="card-white" style="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>📦 {r.iloc[3]} | 🏢 {r.iloc[5]}{btn_ca}</div>""", unsafe_allow_html=True)

# --- TAB 3: MAPA ---
with tab3:
    st.subheader("📍 Ubicación de Camiones Ofertados")
    m = folium.Map(location=[-32.5, -61.5], zoom_start=6, tiles="cartodbpositron")
    for ciudad, coords in COORDS_CIUDADES.items():
        count = len(df_ch_raw[df_ch_raw.iloc[:, 1].str.contains(ciudad, na=False)])
        if count > 0:
            folium.CircleMarker(location=coords, radius=5+(count*3), color="#3498db", fill=True, popup=f"{ciudad}: {count} camiones").add_to(m)
    folium_static(m)

# --- TAB 4: LLEGADA ---
with tab4:
    st.subheader("🚩 Avisar llegada a Ignacio")
    with st.form("llegada"):
        pat = st.text_input("Patente").upper()
        planta = st.selectbox("Planta", list(st.session_state.cupos.keys()))
        if st.form_submit_button("GENERAR AVISO"):
            msg_ll = f"Ignacio, el camión {pat} llegó a descarga en {planta}."
            link_ll = f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg_ll)}"
            st.markdown(f'<a href="{link_ll}" target="_blank" style="background:#238636; color:white; padding:15px; border-radius:8px; text-decoration:none; display:block; text-align:center;">ENVIAR WHATSAPP</a>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
