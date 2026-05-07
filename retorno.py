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

COORDS_CIUDADES = {
    "TODAS": (0,0),
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237), "AVELLANEDA (SF)": (-29.117, -59.658), "CRISPI (SF)": (-31.721, -61.916),
    "SASTRE (SF)": (-31.766, -61.828), "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
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
if "situacion_logistica" not in st.session_state: st.session_state.situacion_logistica = "Sin reportes de demora en puertos."
if "search_query" not in st.session_state: st.session_state.search_query = ""

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
            if refs_a_borrar: df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_a_borrar)]
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except: return pd.DataFrame(), pd.DataFrame(), []

def obtener_clima(ciudad):
    if ciudad == "TODAS": return ""
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True").json()
        temp = res['current_weather']['temperature']
        return f"🌡️ {temp}°C"
    except: return ""

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, o, d, es_ch=True):
    msg = f"Hola! Vi tu {'camion' if es_ch else 'carga'} de {o} a {d} en Retorno Match."
    return f"https://api.whatsapp.com/send?phone={limpiar_wsp(num)}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(ts):
    try:
        dt = pd.to_datetime(ts); diff = datetime.now() - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        h = diff.seconds // 3600
        return f"Hace {h}h" if h > 0 else f"Hace {(diff.seconds % 3600) // 60}m"
    except: return "Reciente"

def calcular_distancia(o, d):
    l1, ln1 = COORDS_CIUDADES.get(o, (0,0))
    l2, ln2 = COORDS_CIUDADES.get(d, (0,0))
    if l1 == 0 or l2 == 0: return 0
    phi1, phi2 = math.radians(l1), math.radians(l2)
    a = math.sin(math.radians(l2-l1)/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(math.radians(ln2-ln1)/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .card-cosecha { background: #1c2a1c; border: 1px solid #2d4d2d; color: #8ebf8e; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #4caf50; position: relative; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; line-height: 1.2; }
    .btn-wsp { background: #238636; color: white !important; padding: 14px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
    .info-bar { background: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #f1e05a; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Gestión")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_logistica = st.text_area("🚛 Situación Actual (Demoras):", st.session_state.situacion_logistica)
        if st.button("♻️ Sincronizar"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios} -- CREADO POR IGNACIO DIAZ</b></marquee></div>', unsafe_allow_html=True)

# Situación Actual y Clima
st.write("")
col_sit, col_cli = st.columns([3, 1])
with col_sit:
    st.markdown(f'<div class="info-bar">⚠️ <b>SITUACIÓN ACTUAL:</b> {st.session_state.situacion_logistica}</div>', unsafe_allow_html=True)

# Filtros Rápidos
col_search, col_fast = st.columns([2, 1])
with col_search:
    busqueda_libre = st.text_input("🔎 BUSCAR:", value=st.session_state.search_query, placeholder="Localidad...").upper()
with col_fast:
    if st.button("🧹 Limpiar"): st.session_state.search_query = ""; st.rerun()

filtro_loc = st.selectbox("📍 Ciudad Base:", list(COORDS_CIUDADES.keys()))
clima_txt = obtener_clima(filtro_loc)
if clima_txt: st.write(f"Estado del tiempo en {filtro_loc}: **{clima_txt}**")

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR CAMIÓN"):
                with st.form("f_ch", clear_on_submit=True):
                    o_p, d_p = st.text_input("Origen").upper(), st.text_input("Destino").upper()
                    eq, ws = st.text_input("Equipo"), st.text_input("WhatsApp")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1574172378": ws})
                        st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ch_raw.empty:
            for idx, r in df_ch_raw.iterrows():
                if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                    st.markdown(f"""<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
<span class="route-txt">📍 {r.iloc[1]} <br>➔ {r.iloc[2]}</span><br>
<b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}
<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" class="btn-wsp">OFERTAR CARGA</a></div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ NUEVA CARGA"):
                with st.form("f_ca", clear_on_submit=True):
                    o, d = st.text_input("Carga").upper(), st.text_input("Descarga").upper()
                    m, en, w = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
                    urg = st.checkbox("🚨 URGENTE")
                    if st.form_submit_button("💼 PUBLICAR"):
                        m_f = f"⚠️URGENTE: {m}" if urg else m
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m_f, "entry.1930562861": en, "entry.466540450": w})
                        st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            for idx, r in df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)].iterrows():
                if busqueda_libre in str(r).upper():
                    estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                    st.markdown(f"""<div class="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
<div class="route-txt">{r.iloc[1]} <br>➔ {r.iloc[2]}</div>
📦 {r.iloc[3]} | 🏢 {r.iloc[5]}
<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" class="btn-wsp" style="background:#2980b9;">SOLICITAR VIAJE</a></div>""", unsafe_allow_html=True)

# --- TAB 4: CALCULADOR ---
with tab4:
    st.subheader("📊 Estimador de Costos")
    o_c = st.selectbox("Desde", list(COORDS_CIUDADES.keys()), key="ca1")
    d_c = st.selectbox("Hasta", list(COORDS_CIUDADES.keys()), key="ca2")
    t_km = st.number_input("Tarifa $/KM", value=1300)
    dist = calcular_distancia(o_c, d_c)
    if dist > 0:
        dist_r = dist * 1.22
        st.metric("Distancia Estimada", f"{dist_r:.0f} KM")
        st.success(f"Total Sugerido: ${dist_r * t_km:,.0f}")

st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
