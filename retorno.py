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
WSP_VENTAS_VIP = "5493401525621"

# --- BASE DE DATOS DE PUEBLOS Y CIUDADES (ACTUALIZADA CON PUERTOS) ---
COORDS_CIUDADES = {
    "TODAS": (0,0),
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237), "AVELLANEDA (SF)": (-29.117, -59.658), "CRISPI (SF)": (-31.721, -61.916),
    "SASTRE (SF)": (-31.766, -61.828), "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
    "PUERTO GRAL SAN MARTIN (SF)": (-32.745, -60.732), "TIMBUES (SF)": (-32.668, -60.751), "SAN LORENZO (SF)": (-32.746, -60.734),
    "VILLA CONSTITUCION (SF)": (-33.227, -60.329), "CORDOBA (CBA)": (-31.413, -64.181), "SAN FRANCISCO (CBA)": (-31.427, -62.082),
    "RIO CUARTO (CBA)": (-33.123, -64.348), "VILLA MARIA (CBA)": (-32.407, -63.240), "JESUS MARIA (CBA)": (-30.981, -64.093),
    "MARCOS JUAREZ (CBA)": (-32.697, -62.106), "BAHIA BLANCA (BA)": (-38.718, -62.266), "QUEQUEN (BA)": (-38.541, -58.713),
    "CAMPANA (BA)": (-34.163, -58.959), "ZARATE (BA)": (-34.096, -59.024), "RAMALLO (BA)": (-33.483, -60.000),
    "PERGAMINO (BA)": (-33.891, -60.573), "PARANA (ER)": (-31.733, -60.529), "VICTORIA (ER)": (-32.624, -60.155),
    "SGO DEL ESTERO": (-27.795, -64.263), "TUCUMAN": (-26.824, -65.222), "SALTA": (-24.785, -65.411)
}

# --- 2. GESTIÓN DE SESIÓN ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "situacion_actual" not in st.session_state: st.session_state.situacion_actual = "Sin reportes de demoras por el momento."
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "favoritos" not in st.session_state: st.session_state.favoritos = []

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

        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
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

def generar_wsp_link(num, origen, destino, es_chofer=True):
    clean_num = limpiar_wsp(num)
    msg = f"Hola! Vi tu {'camión' if es_chofer else 'carga'} de {origen} a {destino} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def obtener_frescura_clase(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff = datetime.now() - dt
        if diff.seconds < 3600: return "fresh-green"
        if diff.seconds < 10800: return "fresh-orange"
        return "fresh-gray"
    except: return "fresh-gray"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        ahora = datetime.now()
        diff = ahora - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        if horas > 0: return f"Hace {horas}h"
        minutos = (diff.seconds % 3600) // 60
        return f"Hace {minutos}m"
    except: return "Reciente"

def calcular_distancia_coord(p1, p2):
    lat1, lon1 = p1
    lat2, lon2 = p2
    if lat1 == 0 or lat2 == 0: return 9999
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    # PROTECCIÓN: Si la ciudad no está en el mapa, devolvemos None en lugar de romper el código
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"
        res = requests.get(url).json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except: return "N/A"

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #adbac7; }
    .card-white { background: linear-gradient(145deg, #1c2128, #22272e); color: #adbac7; padding: 18px; border-radius: 14px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; transition: 0.3s; }
    .card-urgente { background: linear-gradient(145deg, #2d1b1b, #3d1f1f); color: #ff6b6b; padding: 18px; border-radius: 14px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .badge-vip { background: #f1e05a; color: #0d1117; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.7rem; margin-left: 5px; vertical-align: middle; }
    .route-txt { font-size: 1.15rem; font-weight: 800; color: #539bf5; text-transform: uppercase; line-height: 1.2; }
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 12px; border-radius: 10px; margin-bottom: 20px; color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Gestión")
    pin_input = st.text_input("PIN Admin", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual (Demoras):", st.session_state.situacion_actual)
        if st.button("♻️ Forzar Sincronización"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT Acceso VIP:").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL
    
    st.divider()
    st.write("⭐ Mis Favoritos:", len(st.session_state.favoritos))
    if st.button("🗑️ Vaciar Favoritos"): st.session_state.favoritos = []; st.rerun()

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios} -- CREADO POR IGNACIO DIAZ</b></marquee></div>', unsafe_allow_html=True)

# Filtros
col_search, col_radio = st.columns([2, 1.5])
with col_search:
    busqueda_libre = st.text_input("🔎 BUSCAR:", value=st.session_state.search_query, placeholder="Localidad, Empresa...").upper()
with col_radio:
    radio_km = st.slider("📍 Radio de cercanía (KM):", 0, 300, 0)

filtro_loc = st.selectbox("📍 Ciudad Base (Origen):", list(COORDS_CIUDADES.keys()))

# Situación y Clima
st.write("")
col_sit, col_clima = st.columns([3, 1])
with col_sit:
    st.markdown(f'<div class="status-bar">⚠️ <b>SITUACIÓN ACTUAL:</b> {st.session_state.situacion_actual}</div>', unsafe_allow_html=True)
with col_clima:
    ciudad_clima = "SAN JORGE (SF)" if filtro_loc == "TODAS" else filtro_loc
    # Se llama a la función con protección anti-error
    clima_val = obtener_clima(ciudad_clima)
    if clima_val:
        st.markdown(f'<div class="status-bar" style="border-left-color:#3498db; text-align:center;">{clima_val}<br><small>{ciudad_clima}</small></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 RENTABILIDAD"])

# --- TAB 1: CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        for idx, r in df_ch_raw.iterrows():
            dist_km = calcular_distancia_coord(COORDS_CIUDADES.get(filtro_loc, (0,0)), COORDS_CIUDADES.get(str(r.iloc[1]), (0,0)))
            if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or (radio_km == 0 or dist_km <= radio_km)):
                badge_verificado = '<span class="badge-vip">⭐ VERIFICADO</span>' if str(r.iloc[4]).strip() in LISTA_VIPS_GLOBAL else ""
                st.markdown(f"""<div class="card-white">
                    <span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span> {badge_verificado}<br>
                    <b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}
                    <a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" style="background: #238636; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px;">OFERTAR CARGA</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for idx, r in df_ca_v.iterrows():
            dist_km = calcular_distancia_coord(COORDS_CIUDADES.get(filtro_loc, (0,0)), COORDS_CIUDADES.get(str(r.iloc[1]), (0,0)))
            if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or (radio_km == 0 or dist_km <= radio_km)):
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                st.markdown(f"""<div class="{estilo}">
                    <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                    📦 <b>{r.iloc[3]}</b> | 🏢 {r.iloc[5]}
                    <a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" style="background:#2980b9; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px;">SOLICITAR VIAJE</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 4: RENTABILIDAD (CON PUERTOS HABILITADOS) ---
with tab4:
    st.subheader("📈 Calculador de Rentabilidad Real")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        punto_a = st.selectbox("Desde:", list(COORDS_CIUDADES.keys()), index=1)
        punto_b = st.selectbox("Hasta (Puerto/Destino):", list(COORDS_CIUDADES.keys()), index=12) # Index 12 es PTO SAN MARTIN
        toneladas = st.number_input("Toneladas", value=30)
    with col_c2:
        tarifa = st.number_input("Tarifa por Tonelada ($)", value=25000)
        gasoil = st.number_input("Precio Gasoil ($/L)", value=1100)

    # Cálculo seguro con coordenadas mapeadas
    coord_a = COORDS_CIUDADES.get(punto_a, (0,0))
    coord_b = COORDS_CIUDADES.get(punto_b, (0,0))
    dist = calcular_distancia_coord(coord_a, coord_b)
    
    if dist > 0 and dist < 9999:
        km_reales = dist * 1.25
        ingreso = tarifa * toneladas
        gasto_fuego = (km_reales / 100) * 40 * gasoil
        neta = ingreso - gasto_fuego - (ingreso * 0.07)
        
        st.divider()
        st.metric("Distancia Estimada", f"{km_reales:.0f} KM")
        st.success(f"GANANCIA ESTIMADA: ${neta:,.0f}")

# --- FOOTER ---
st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
