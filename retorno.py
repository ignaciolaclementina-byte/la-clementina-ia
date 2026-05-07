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
# Reemplaza el ID de abajo con el de tu formulario de habilitación CUIT si lo usas
URL_VIP_POST = "https://docs.google.com/forms/d/e/1FAIpQLSfYourFormIDHere/formResponse"

ADMIN_PIN = "1323" 
WSP_VENTAS_VIP = "5493401525621"

# --- BASE DE DATOS DE CIUDADES ---
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
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "anuncios" not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "situacion_actual" not in st.session_state:
    st.session_state.situacion_actual = "Operativa normal en puertos."
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Lógica de borrado automático por referencia
        if not df_ca.empty:
            mask_borrado = (df_ca.iloc[:, 1].astype(str).str.contains('BORRADO', case=False))
            refs_a_borrar = [re.search(r'REF:(.*)', str(cell)).group(1).strip() for row in df_ca[mask_borrado].values for cell in row if re.search(r'REF:(.*)', str(cell))]
            df_ca = df_ca[~mask_borrado]
            if refs_a_borrar:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_a_borrar)]

        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except:
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

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        ahora = datetime.now()
        diff = ahora - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        if horas > 0: return f"Hace {horas}h"
        return f"Hace {(diff.seconds % 3600) // 60}m"
    except: return "Reciente"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        return f"🌡️ {res['current_weather']['temperature']}°C"
    except: return "N/A"

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
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #e6edf3; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (PANEL DE GESTIÓN) ---
with st.sidebar:
    st.title("🛡️ Gestión")
    pin_input = st.text_input("PIN Admin", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        
        st.subheader("⭐ Panel VIP")
        with st.form("f_vip", clear_on_submit=True):
            v_cuit = st.text_input("Habilitar CUIT:").strip()
            if st.form_submit_button("✅ HABILITAR"):
                if v_cuit:
                    requests.post(URL_VIP_POST, data={"entry.123456789": v_cuit}) # Ajustar entry ID
                    st.cache_data.clear(); st.rerun()

        st.session_state.anuncios = st.text_area("📢 Mensajes Banner:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Situación:", st.session_state.situacion_actual)
        if st.button("♻️ Forzar Sincronización"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT Acceso VIP:").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# --- CABECERA (BANNER LIMPIO) ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# Filtros y Clima
st.write("")
col_search, col_clima = st.columns([3, 1])
with col_search:
    busqueda_libre = st.text_input("🔎 BUSCAR:", value=st.session_state.search_query, placeholder="Ciudad, Mercadería, Empresa...").upper()
with col_clima:
    clima_val = obtener_clima("SAN JORGE (SF)")
    st.markdown(f'<div class="status-bar" style="border-left-color:#3498db; text-align:center; margin-bottom:0;">{clima_val}<br><small>SAN JORGE</small></div>', unsafe_allow_html=True)

st.markdown(f'<div class="status-bar" style="margin-top:10px;">⚠️ <b>SITUACIÓN ACTUAL:</b> {st.session_state.situacion_actual}</div>', unsafe_allow_html=True)

# --- PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 RENTABILIDAD"])

# --- TAB 1: CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        for idx, r in df_ch_raw.iterrows():
            if busqueda_libre in str(r).upper():
                st.markdown(f"""<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                <span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br>
                <b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5]) if not es_user_vip else r.iloc[5]}
                <a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2], True)}" style="background: #238636; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px; font-weight: bold;">OFERTAR CARGA</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for idx, r in df_ca_v.iterrows():
            if busqueda_libre in str(r).upper():
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                st.markdown(f"""<div class="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                📦 <b>{r.iloc[3]}</b> | 🏢 {r.iloc[5]}
                <a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" style="background:#2980b9; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px; font-weight: bold;">SOLICITAR VIAJE</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for idx, r in df_arr.iterrows():
            if busqueda_libre in str(r).upper():
                st.markdown(f"""<div class="card-cosecha"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                <b>📍 ZONA: {r.iloc[2]}</b><br>🌾 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4]) if not es_user_vip else r.iloc[4]}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" style="background: #238636; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; margin-top: 10px; font-weight: bold;">CONTACTAR</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 4: RENTABILIDAD (MEJORADA) ---
with tab4:
    st.subheader("📊 Calculador de Rentabilidad Real")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        o_c = st.selectbox("Desde", list(COORDS_CIUDADES.keys()), key="rent1")
        d_c = st.selectbox("Hasta", list(COORDS_CIUDADES.keys()), key="rent2")
        tarifa = st.number_input("Tarifa por Tonelada ($)", value=15000)
    with c_col2:
        gasoil = st.number_input("Gasoil ($/Litro)", value=1100)
        comi = st.slider("Comisión Agencia (%)", 0, 15, 7)
    
    dist = calcular_distancia(o_c, d_c) * 1.22 # Factor de corrección de ruta
    if dist > 0:
        gastos_gasoil = (dist / 100 * 40) * gasoil # Asumiendo 40L/100km
        ingreso_neto = (tarifa * 30) * (1 - comi/100)
        margen = ingreso_neto - gastos_gasoil
        
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Distancia", f"{dist:.0f} KM")
        m2.metric("Gasto Estimado Combustible", f"${gastos_gasoil:,.0f}")
        m3.metric("Margen Estimado (30tn)", f"${margen:,.0f}", delta=f"{margen/ingreso_neto*100:.1f}%")

# --- FOOTER ---
st.markdown("<div style='text-align:center; padding:20px; opacity:0.5; font-size:0.8rem;'>Creado por Ignacio Diaz - 2026</div>", unsafe_allow_html=True)
