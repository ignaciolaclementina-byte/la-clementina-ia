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
for key, val in {"admin_mode": False, "anuncios": "¡Bienvenido!", "situacion_actual": "Normal", "search_query": "", "reportes_puerto": ""}.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. CARGA DE DATOS (CORREGIDO PARA MOSTRAR TODO) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Limpieza de borrados: busca la palabra en cualquier parte de la fila
        if not df_ca.empty:
            df_ca = df_ca[~df_ca.apply(lambda row: row.astype(str).str.contains('BORRADO', case=False).any(), axis=1)]

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
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    msg = f"Hola! Vi tu camión de {origen} a {destino}" if es_chofer else f"Me interesa la carga {origen} -> {destino}"
    return f"https://api.whatsapp.com/send?phone={limpiar_wsp(num)}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text=Solicito VIP CUIT: {cuit}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str); diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        return f"Hace {diff.seconds // 3600}h" if diff.seconds // 3600 > 0 else f"Hace {diff.seconds // 60}m"
    except: return "Reciente"

def calcular_distancia(o, d):
    p1, p2 = COORDS_CIUDADES.get(o, (0,0)), COORDS_CIUDADES.get(d, (0,0))
    if p1 == (0,0) or p2 == (0,0): return 0
    a = math.sin(math.radians(p2[0]-p1[0])/2)**2 + math.cos(math.radians(p1[0]))*math.cos(math.radians(p2[0]))*math.sin(math.radians(p2[1]-p1[1])/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    try:
        lat, lon = COORDS_CIUDADES.get(ciudad, COORDS_CIUDADES["SAN JORGE (SF)"])
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        return f"🌡️ {res['current_weather']['temperature']}°C"
    except: return "N/A"

# --- 5. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #ff4b4b; position: relative; }
    .card-cosecha { background: #1c2a1c; border: 1px solid #2d4d2d; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #4caf50; position: relative; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.7rem; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual:", st.session_state.situacion_actual)
        if st.button("♻️ Forzar Sincronización"): st.cache_data.clear(); st.rerun()

st.title("🚛 RETORNO MATCH VIP")
st.info(f"📢 {st.session_state.anuncios}")

user_cuit = st.text_input("Ingrese su CUIT:", key="cuit_input").strip()
es_user_vip = user_cuit in LISTA_VIPS_GLOBAL or st.session_state.admin_mode
lock_btn_html = f'<div style="background: #333; color: #f1c40f; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #f1c40f; font-size:0.8rem;">⭐ ACCESO VIP REQUERIDO</div>'

busqueda_libre = st.text_input("🔎 BUSCAR:", value=st.session_state.search_query).upper()
filtro_loc = st.selectbox("📍 Filtrar por Ciudad Base:", list(COORDS_CIUDADES.keys()))

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

# --- TABS ---
with tab1: # CAMIONES
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" target="_blank" style="background: #238636; color: white; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center;">OFERTAR</a>' if es_user_vip else lock_btn_html
                st.markdown(f'<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br><b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}{btn}</div>', unsafe_allow_html=True)

with tab2: # CARGAS (Filtrando para que NO aparezca Arrime)
    if not df_ca_raw.empty:
        df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.upper().str.contains('ARRIME', na=False)]
        for _, r in df_ca_v.iterrows():
            if busqueda_libre in str(r).upper():
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                btn = f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" style="background:#2980b9; color: white; padding: 10px; border-radius: 8px; text-decoration: none; display:block; text-align: center;">SOLICITAR</a>' if es_user_vip else lock_btn_html
                st.markdown(f'<div class="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>{r.iloc[3]}</b> | {r.iloc[5]}{btn}</div>', unsafe_allow_html=True)

with tab3: # COSECHA (CORREGIDO PARA DETECTAR 'ARRIME ZONA')
    st.markdown('<div class="card-cosecha">🚜 <b>INDICADOR DE DENSIDAD DE COSECHA: 85%</b></div>', unsafe_allow_html=True)
    if not df_ca_raw.empty:
        # Buscamos 'ARRIME' en mayúsculas para asegurar detección según image_77c334.png
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.upper().str.contains('ARRIME', na=False)]
        for _, r in df_arr.iterrows():
            if busqueda_libre in str(r).upper():
                btn = f'<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" style="background: #238636; color: white; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center;">CONTACTAR</a>' if es_user_vip else lock_btn_html
                st.markdown(f'<div class="card-cosecha"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><div style="font-weight:bold;">📍 ZONA: {r.iloc[2]}</div>🌾 {r.iloc[3]}{btn}</div>', unsafe_allow_html=True)

with tab4: # COSTOS
    st.write(f"Distancia: {calcular_distancia(st.selectbox('Origen', list(COORDS_CIUDADES.keys()), key='c1'), st.selectbox('Destino', list(COORDS_CIUDADES.keys()), key='c2')) * 1.22:.0f} KM")

st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
