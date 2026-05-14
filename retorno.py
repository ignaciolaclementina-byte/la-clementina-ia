import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import pydeck as pdk # Agregamos para el Mapa de Calor

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
        
        if not df_ca.empty:
            mask_borrado = (df_ca.iloc[:, 1].astype(str).str.contains('BORRADO', case=False))
            refs_a_borrar = [re.search(r'REF:(.*)', str(cell)).group(1).strip() for row in df_ca[mask_borrado].values for cell in row if re.search(r'REF:(.*)', str(cell))]
            df_ca = df_ca[~mask_borrado]
            if refs_a_borrar:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_a_borrar)]

        vips = []
        try:
            url_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
            df_v = pd.read_csv(url_vip, header=None)
            if not df_v.empty: vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass
        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True, reporte_llegada=False):
    clean_num = limpiar_wsp(num)
    if reporte_llegada:
        msg = f"Ignacio, ya estoy en destino ({destino}). Mi ubicación actual es: https://www.google.com/maps/search/?api=1&query={COORDS_CIUDADES.get(destino, (0,0))[0]},{COORDS_CIUDADES.get(destino, (0,0))[1]}"
    else:
        msg = f"Hola! Vi tu anuncio de {origen} a {destino} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    msg = f"Hola Ignacio! Quiero solicitar el acceso VIP para el CUIT: {cuit}"
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        return f"Hace {horas}h" if horas > 0 else f"Hace {(diff.seconds % 3600) // 60}m"
    except: return "Reciente"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    a = math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        temp = res['current_weather']['temperature']
        code = res['current_weather']['weathercode']
        # Semáforo de color por código de clima
        emoji = "🔴" if code >= 51 else "🟢"
        return f"{emoji} {temp}°C"
    except: return "N/A"

def generar_reporte_puertos_real():
    if st.session_state.reportes_puerto and st.session_state.reportes_puerto.strip() != "":
        return f"🚨 AVISO ADMIN: {st.session_state.reportes_puerto}"
    puertos = ["TIMBUES (SF)", "PTO GRAL SAN MARTIN (SF)", "SAN LORENZO (SF)"]
    estados = [f"{p.split(' ')[0]}: {obtener_clima(p)}" for p in puertos]
    return " | ".join(estados)

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .card-cosecha { background: #1c2a1c; border: 1px solid #2d4d2d; color: #8ebf8e; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #4caf50; position: relative; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual:", st.session_state.situacion_actual)
        st.session_state.reportes_puerto = st.text_area("🚢 Reporte Puertos:", st.session_state.reportes_puerto)
    else: st.session_state.admin_mode = False

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")

# --- ALERTA COSECHA (Mejora solicitada) ---
if datetime.now().month in [3, 4, 5]:
    st.warning("🌾 **ALERTA COSECHA GRUESA:** Se detecta alta demanda. Priorice viajes con cupo confirmado.")

# --- SECCIÓN VIP ---
user_cuit = st.text_input("Ingrese CUIT:", key="cuit_input").strip()
es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# --- REPORTE DE PUERTOS (Mejora: Semáforos) ---
st.markdown(f'<div class="status-bar">🚢 **CUPOS:** {generar_reporte_puertos_real()}</div>', unsafe_allow_html=True)

# Filtros Rápidos
busqueda_libre = st.text_input("🔎 BUSCAR (Localidad, Empresa...):").upper()
filtro_loc = st.selectbox("📍 Ciudad Base:", list(COORDS_CIUDADES.keys()))

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

# --- TAB 1: CAMIONES (Mejora: Mapa de Calor) ---
with tab1:
    if not df_ch_raw.empty:
        # Lógica de Mapa de Calor
        map_points = []
        for loc in df_ch_raw.iloc[:, 1].unique():
            if loc in COORDS_CIUDADES:
                count = len(df_ch_raw[df_ch_raw.iloc[:, 1] == loc])
                lat, lon = COORDS_CIUDADES[loc]
                map_points.append({"lat": lat, "lon": lon, "weight": count})
        
        if map_points:
            with st.expander("📍 VER MAPA DE CONCENTRACIÓN DE CAMIONES"):
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/dark-v9',
                    initial_view_state=pdk.ViewState(latitude=-31.8, longitude=-61.8, zoom=6, pitch=40),
                    layers=[pdk.Layer('HeatmapLayer', data=map_points, get_position='[lon, lat]', get_weight='weight', radius_pixels=60)]
                ))

    col1, col2 = st.columns([1, 2.2])
    with col2:
        for idx, r in df_ch_raw.iterrows():
            if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2], True)}" target="_blank" style="background:#238636; color:white; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center;">OFERTAR CARGA</a>' if es_user_vip else "🔒 Bloqueado"
                st.markdown(f'<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</span><br><b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}{btn}</div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS (Mejora: Botón Llegué) ---
with tab2:
    for idx, r in df_ca_raw.iterrows():
        if "ARRIME" not in str(r.iloc[1]) and busqueda_libre in str(r).upper():
            estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
            btn_wsp = f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" style="background:#2980b9; color:white; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center; flex:2;">SOLICITAR VIAJE</a>' if es_user_vip else "🔒 Acceso VIP"
            btn_llegue = f'<a href="{generar_wsp_link(WSP_VENTAS_VIP, r.iloc[1], r.iloc[2], reporte_llegada=True)}" target="_blank" style="background:#30363d; color:#539bf5; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center; flex:1; border:1px solid #539bf5;">✅ LLEGUÉ</a>'
            
            st.markdown(f'<div class="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>{r.iloc[3]} | {r.iloc[5]}<div style="display:flex; gap:10px; margin-top:10px;">{btn_wsp}{btn_llegue}</div></div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA (Arrimes) ---
with tab3:
    df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
    for idx, r in df_arr.iterrows():
        if busqueda_libre in str(r).upper():
            btn = f'<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" style="background:#238636; color:white; padding:10px; border-radius:8px; text-decoration:none; display:block; text-align:center;">CONTACTAR</a>' if es_user_vip else "🔒 Bloqueado"
            st.markdown(f'<div class="card-cosecha">📍 ZONA: {r.iloc[2]}<br>{r.iloc[3]}{btn}</div>', unsafe_allow_html=True)

# --- TAB 4: CALCULADOR ---
with tab4:
    o_c, d_c = st.selectbox("Desde", list(COORDS_CIUDADES.keys()), key="c1"), st.selectbox("Hasta", list(COORDS_CIUDADES.keys()), key="c2")
    dist = calcular_distancia(o_c, d_c) * 1.22
    if dist > 0:
        st.metric("Distancia Estimada", f"{dist:.0f} KM")
        st.success(f"Costo Sugerido ($1300/km): ${dist * 1300:,.0f}")

st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
