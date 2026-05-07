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
if "search_query" not in st.session_state: st.session_state.search_query = ""
if "modo_ruta" not in st.session_state: st.session_state.modo_ruta = False

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
        st.error(f"Error de conexión: {e}"); return pd.DataFrame(), pd.DataFrame(), []

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

def link_google_maps(origen, destino):
    return f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(origen)}&destination={urllib.parse.quote(destino)}&travelmode=driving"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        diff = datetime.now() - dt
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

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# Estilos dinámicos para Modo Ruta
font_size = "1.3rem" if st.session_state.modo_ruta else "1.1rem"
card_padding = "20px" if st.session_state.modo_ruta else "15px"

st.markdown(f"""
<style>
    .stApp {{ background-color: #0e1117; color: #adbac7; }}
    .card-white {{ background: #1c2128; color: #adbac7; padding: {card_padding}; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }}
    .card-urgente {{ background: #2d1b1b; color: #ff6b6b; padding: {card_padding}; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }}
    .badge-time {{ position: absolute; top: 10px; right: 10px; font-size: 0.75rem; background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e; }}
    .badge-cupo {{ background: #f39c12; color: black; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; margin-left: 10px; }}
    .route-txt {{ font-size: {font_size}; font-weight: 800; color: #539bf5; text-transform: uppercase; line-height: 1.2; }}
    .btn-wsp {{ background: #238636; color: white !important; padding: 14px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; font-size: 1rem; }}
    .btn-maps {{ background: #30363d; color: #adbac7 !important; padding: 8px; border-radius: 6px; text-decoration: none; display: inline-block; text-align: center; font-size: 0.8rem; margin-top: 5px; border: 1px solid #444; }}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Panel Control")
    if st.text_input("PIN Admin", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR")
        st.session_state.anuncios = st.text_area("📢 Anuncio:", st.session_state.anuncios)
        if st.button("♻️ Sincronizar"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False
    
    st.divider()
    st.session_state.modo_ruta = st.toggle("🚚 MODO RUTA (Letra Grande)", value=st.session_state.modo_ruta)
    user_cuit = st.text_input("🔑 CUIT VIP:").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios} -- CREADO POR IGNACIO DIAZ</b></marquee></div>', unsafe_allow_html=True)

# Filtros e Insights
st.write("")
col_s, col_l = st.columns([2, 1])
busqueda_libre = col_s.text_input("🔎 BUSCAR:", value=st.session_state.search_query).upper()
if col_l.button("🧹 Limpiar"): st.session_state.search_query = ""; st.rerun()

st.write("Accesos Rápidos:")
r1, r2, r3, r4 = st.columns(4)
if r1.button("🚢 PUERTOS"): st.session_state.search_query = "PUERTO"; st.rerun()
if r2.button("🌻 ACEITERAS"): st.session_state.search_query = "COFCO"; st.rerun()
if r3.button("📍 MI ZONA"): st.session_state.search_query = "SAN JORGE"; st.rerun()
if r4.button("⭐ FAVORITOS"): st.session_state.search_query = "VIP"; st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR"):
                with st.form("f_ch", clear_on_submit=True):
                    o, d = st.text_input("Origen").upper(), st.text_input("Destino").upper()
                    eq, cu, ws = st.text_input("Equipo"), st.text_input("CUIT"), st.text_input("WhatsApp")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                        st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iterrows():
                if busqueda_libre in str(r).upper():
                    st.markdown(f"""<div class="card-white">
                    <div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                    <span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br>
                    <b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}<br>
                    <a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2])}" class="btn-wsp">OFERTAR</a>
                    </div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ NUEVA CARGA"):
                with st.form("f_ca", clear_on_submit=True):
                    o, d = st.text_input("Carga").upper(), st.text_input("Descarga").upper()
                    m, en, w = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
                    cupos = st.number_input("Cupos", min_value=1, value=1)
                    if st.form_submit_button("💼 PUBLICAR"):
                        m_v = f"{m} (CUPOS:{cupos})"
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m_v, "entry.1930562861": en, "entry.466540450": w})
                        st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            for _, r in df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME')].iterrows():
                if busqueda_libre in str(r).upper():
                    estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                    cupo_label = re.search(r'CUPOS:(\d+)', str(r.iloc[3]))
                    cupo_html = f'<span class="badge-cupo">CUPOS: {cupo_label.group(1)}</span>' if cupo_label else ""
                    st.markdown(f"""<div class="{estilo}">
                    <div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                    <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]} {cupo_html}</div>
                    📦 {r.iloc[3]} | 🏢 {r.iloc[5]}<br>
                    <a href="{link_google_maps(r.iloc[1], r.iloc[2])}" class="btn-maps" target="_blank">🗺️ Ver Hoja de Ruta</a>
                    <a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" class="btn-wsp" style="background:#2980b9;">PEDIR VIAJE</a>
                    </div>""", unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME')]
        for _, r in df_arr.iterrows():
            if busqueda_libre in str(r).upper():
                st.markdown(f"""<div class="card-cosecha">
                <div class="badge-time">{formatear_fecha(r.iloc[0])}</div>
                <b>📍 ZONA: {r.iloc[2]}</b><br>🌾 {r.iloc[3]}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONTACTAR</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 4: CALCULADOR ---
with tab4:
    o_c = st.selectbox("Origen", list(COORDS_CIUDADES.keys()))
    d_c = st.selectbox("Destino", list(COORDS_CIUDADES.keys()))
    dist = calcular_distancia(o_c, d_c)
    if dist > 0:
        dist_f = dist * 1.22
        st.metric("Distancia Estimada", f"{dist_f:.0f} KM")
        st.info(f"💡 Sugerencia: El precio promedio en esta ruta es de $1.450/KM")

# --- FOOTER ---
st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
