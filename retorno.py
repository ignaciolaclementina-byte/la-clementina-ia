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
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES MEJORADAS ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num, es_vip):
    if es_vip or st.session_state.admin_mode: return str(num).split('.')[0]
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def calcular_tiempo(timestamp_str):
    try:
        # Formato estándar de Google Forms: "day/month/year hour:min:sec"
        dt = pd.to_datetime(timestamp_str)
        dif = datetime.now() - dt
        if dif.days > 0: return f"Hace {dif.days}d"
        horas = dif.seconds // 3600
        if horas > 0: return f"Hace {horas}h"
        return f"Hace {dif.seconds // 60}m"
    except: return "Reciente"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.9)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card-white { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; position: relative; }
    .card-cosecha { background: #f1f8e9; border: 2px solid #4caf50; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .badge-vip { background: #f1c40f; color: black; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; }
    .time-txt { position: absolute; top: 10px; right: 15px; font-size: 11px; color: #7f8c8d; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; transition: 0.3s; }
    .btn-wsp:hover { background: #128C7E; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("🛡️ Gestión Central")
    pin_input = st.text_input("PIN de Administrador:", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Radar de Mensajes:", st.session_state.anuncios)
        if st.button("♻️ Forzar Sincronización"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT Acceso VIP:").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL
    if es_user_vip: st.warning("✨ ACCESO VIP ACTIVADO")

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#e74c3c; padding:12px; border-radius:12px; text-align:center;"><marquee scrollamount="8"><b>{st.session_state.anuncios} -- CREADO POR IGNACIO DIAZ</b></marquee></div>', unsafe_allow_html=True)

# Filtros
st.write("")
c_f1, c_f2 = st.columns([2, 1])
with c_f1:
    busqueda_libre = st.text_input("🔎 Buscar Localidad, Empresa o Destino:", placeholder="Ej: PUERTO, COFCO, MAIZ...").upper()
with c_f2:
    filtro_loc = st.selectbox("📍 Ciudad Base (Filtro):", list(COORDS_CIUDADES.keys()))

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA / ARRIME", "📊 CALCULADOR"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.markdown("### 📝 Registrar Camión")
            with st.form("f_ch", clear_on_submit=True):
                o_p = st.text_input("Origen (Ej: SAN JORGE)").upper()
                d_p = st.text_input("Destino (Ej: PUERTO TIMBUES)").upper()
                eq = st.text_input("Tipo de Equipo")
                cu = st.text_input("CUIT Dueño")
                ws = st.text_input("WhatsApp")
                if st.form_submit_button("🚀 PUBLICAR"):
                    if o_p and d_p:
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                        st.cache_data.clear(); st.rerun()
        
        # Mejora: Match automático para el transportista
        if not df_ca_raw.empty and filtro_loc != "TODAS":
            st.markdown(f"#### 🎯 Match para {filtro_loc}")
            matches = df_ca_raw[df_ca_raw.iloc[:, 1].str.contains(filtro_loc, case=False, na=False)]
            if not matches.empty:
                st.info(f"Hay {len(matches)} cargas saliendo de tu zona.")

    with c2:
        if not df_ch_raw.empty:
            for idx, r in df_ch_raw.iterrows():
                if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                    es_vip_item = str(r.iloc[4]) in LISTA_VIPS_GLOBAL
                    check_icon = "✅" if es_vip_item else ""
                    st.markdown(f"""<div class="card-white">
                    <span class="time-txt">🕒 {calcular_tiempo(r.iloc[0])}</span>
                    <span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]} {check_icon}</span><br>
                    <b>EQUIPO:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5], es_user_vip)}
                    {"<span class='badge-vip'>Socio VIP</span>" if es_vip_item else ""}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}&text=Hola,%20vi%20tu%20camion%20en%20Retorno%20Match%20de%20{r.iloc[1]}%20a%20{r.iloc[2]}" class="btn-wsp">OFERTAR CARGA</a>
                    </div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.markdown("### 📝 Nueva Carga")
            with st.form("f_ca", clear_on_submit=True):
                o = st.text_input("Punto de Carga").upper()
                d = st.text_input("Punto de Descarga").upper()
                m = st.text_input("Mercadería")
                en = st.text_input("Empresa")
                w = st.text_input("WhatsApp")
                urg = st.checkbox("🚨 MARCAR URGENTE")
                if st.form_submit_button("💼 PUBLICAR"):
                    if o and d:
                        m_f = f"⚠️URGENTE: {m}" if urg else m
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m_f, "entry.1930562861": en, "entry.466540450": w})
                        st.cache_data.clear(); st.rerun()

    with c2:
        if not df_ca_raw.empty:
            df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
            for idx, r in df_ca_v.iterrows():
                if busqueda_libre in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                    urgente = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                    st.markdown(f"""<div class="{urgente}">
                    <span class="time-txt">🕒 {calcular_tiempo(r.iloc[0])}</span>
                    <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                    📦 {r.iloc[3]} | 🏢 {r.iloc[5]}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}&text=Hola,%20me%20interesa%20la%20carga%20de%20{r.iloc[1]}%20a%20{r.iloc[2]}" class="btn-wsp">SOLICITAR VIAJE</a>
                    </div>""", unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.markdown("### 🌾 Registrar Arrime")
            with st.form("f_arr", clear_on_submit=True):
                loc_arr = st.text_input("📍 Localidad / Zona").upper()
                det_arr = st.text_input("Detalle")
                wsp_arr = st.text_input("WhatsApp")
                if st.form_submit_button("🌾 PUBLICAR"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": loc_arr, "entry.576675281": det_arr, "entry.466540450": wsp_arr})
                    st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
            for idx, r in df_arr.iterrows():
                if busqueda_libre in str(r).upper():
                    st.markdown(f"""<div class="card-cosecha">
                    <span class="time-txt">🕒 {calcular_tiempo(r.iloc[0])}</span>
                    <div style="font-weight:bold; font-size:22px;">📍 ZONA: {r.iloc[2]}</div>
                    🌾 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4], es_user_vip)}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#4caf50;">CONTACTAR</a>
                    </div>""", unsafe_allow_html=True)

# --- TAB 4: CALCULADOR ---
with tab4:
    st.subheader("📊 Centro de Costos")
    c_c1, c_c2 = st.columns(2)
    with c_c1:
        o_c = st.selectbox("Desde", list(COORDS_CIUDADES.keys()), key="ca1")
        d_c = st.selectbox("Hasta", list(COORDS_CIUDADES.keys()), key="ca2")
        t_km = st.number_input("Tarifa sugerida $/KM", value=1300)
    with c_c2:
        dist = calcular_distancia(o_c, d_c)
        if dist > 0:
            dist_r = dist * 1.22
            st.success(f"Distancia Estimada: {dist_r:.0f} KM")
            st.metric("Total Viaje", f"${dist_r * t_km:,.0f}")
            st.info("Nota: La distancia incluye un 22% de desvío logístico estándar.")

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; padding:30px; opacity:0.6;'><b>Creado por Ignacio Diaz - {datetime.now().year}</b></div>", unsafe_allow_html=True)
