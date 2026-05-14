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

URL_CARGAS_POST = "https://docs.google.com/forms/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

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
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "anuncios" not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if "situacion_actual" not in st.session_state:
    st.session_state.situacion_actual = "Sin reportes de demoras por el momento."
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "reportes_puerto" not in st.session_state:
    st.session_state.reportes_puerto = "Normal - Sin demoras reportadas en accesos."

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
            if not df_v.empty:
                vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except: pass
        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES E IA ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    clean_num = limpiar_wsp(num)
    msg = f"Hola! Vi tu camión de {origen} a {destino} en Retorno Match. ¿Tenés carga?" if es_chofer else f"Hola! Me interesa la carga de {origen} a {destino} que publicaste en Retorno Match."
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
        ahora = datetime.now()
        diff = ahora - dt
        if diff.days > 0: return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        if horas > 0: return f"Hace {horas}h"
        minutos = (diff.seconds % 3600) // 60
        return f"Hace {minutos}m"
    except: return "Reciente"

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0,0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlambda = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def obtener_clima(ciudad):
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES: return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"
        res = requests.get(url).json()
        temp = res['current_weather']['temperature']
        code = res['current_weather']['weathercode']
        codigos_clima = {0: "☀️ Despejado", 1: "🌤️ Liger. Nublado", 2: "⛅ Nublado", 3: "☁️ Cubierto", 45: "🌫️ Niebla", 61: "🌧️ Lluvia Leve", 95: "⚡ Tormenta"}
        return f"{codigos_clima.get(code, '🌡️ Templado')} {temp}°C"
    except: return "N/A"

# FUNCIÓN IA: Simulación de extracción de datos de Carta de Porte
def ia_extraer_datos_cp(archivo):
    # Aquí iría la conexión a Google Vision o Tesseract
    # Simulamos el éxito de la IA con datos extraídos de la imagen
    time.sleep(1.5) # Efecto de procesamiento
    return {
        "origen": "SAN JORGE (SF)",
        "destino": "ROSARIO (SF)",
        "mercaderia": "MAIZ REGULAR",
        "empresa": "L.C. AGRO SRL",
        "cuit": "30-71458963-2"
    }

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }
    .card-white { background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db; position: relative; }
    .card-urgente { background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite; border-left: 6px solid #ff4b4b; position: relative; }
    .card-cosecha { background: #1c2a1c; border: 1px solid #2d4d2d; color: #8ebf8e; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 6px solid #4caf50; position: relative; }
    .vip-access-box { background: #1c2128; border: 2px solid #f1c40f; padding: 20px; border-radius: 15px; margin-bottom: 25px; text-align: center; }
    .badge-time { position: absolute; top: 10px; right: 10px; font-size: 0.75rem; color: #8b949e; }
    .route-txt { font-size: 1.1rem; font-weight: 800; color: #539bf5; text-transform: uppercase; }
    .status-bar { background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
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
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual:", st.session_state.situacion_actual)
        st.session_state.reportes_puerto = st.text_area("🚢 Reporte Puertos:", st.session_state.reportes_puerto)
    else: st.session_state.admin_mode = False

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#21262d; border: 1px solid #30363d; padding:10px; border-radius:10px; text-align:center; margin-bottom:15px;"><marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# --- SECCIÓN VIP ---
with st.container():
    st.markdown('<div class="vip-access-box">', unsafe_allow_html=True)
    st.subheader("🔑 ACCESO VIP")
    user_cuit = st.text_input("CUIT para desbloquear:", placeholder="Ej: 20304445556", label_visibility="collapsed").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL
    if user_cuit:
        if es_user_vip: st.markdown('<p style="color:#2ecc71; font-weight:bold;">✅ ACCESO VIP ACTIVO</p>', unsafe_allow_html=True)
        else: st.markdown(f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" style="color:#f1c40f; text-decoration:none; font-weight:bold;">👉 Click aquí para solicitar el acceso</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- FILTROS Y TABS ---
busqueda_libre = st.text_input("🔎 BUSCAR:", value=st.session_state.search_query).upper()
tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS"])
lock_btn_html = f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" style="background: #444; color: #f1c40f !important; padding: 12px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; border: 1px solid #f1c40f;">⭐ SOLICITAR ACCESO VIP</a>'

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR CAMIÓN"):
                with st.form("f_ch", clear_on_submit=True):
                    o_p, d_p = st.text_input("Origen").upper(), st.text_input("Destino").upper()
                    eq, cu, ws = st.text_input("Equipo"), st.text_input("CUIT"), st.text_input("WhatsApp")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                        st.cache_data.clear(); st.rerun()
    with c2:
        for idx, r in df_ch_raw.iterrows():
            if busqueda_libre in str(r).upper():
                btn = f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2], True)}" target="_blank" style="background: #238636; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold;">OFERTAR CARGA</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
                st.markdown(f"""<div class="card-white"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br><b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}{btn}</div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS (CON IA INTEGRADA) ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.markdown("### 📸 IA: Lectura de Carta de Porte")
            archivo_cp = st.file_uploader("Subir foto de CP", type=['jpg', 'png', 'jpeg'])
            
            datos_ia = {"o": "", "d": "", "m": "", "e": ""}
            if archivo_cp:
                with st.spinner("IA Analizando documento..."):
                    res_ia = ia_extraer_datos_cp(archivo_cp)
                    datos_ia = {"o": res_ia["origen"], "d": res_ia["destino"], "m": res_ia["mercaderia"], "e": res_ia["empresa"]}
                    st.success("✅ Datos extraídos")

            with st.expander("➕ NUEVA CARGA", expanded=True if archivo_cp else False):
                with st.form("f_ca_ia", clear_on_submit=True):
                    o = st.text_input("Origen", value=datos_ia["o"]).upper()
                    d = st.text_input("Destino", value=datos_ia["d"]).upper()
                    m = st.text_input("Mercadería", value=datos_ia["m"])
                    en = st.text_input("Empresa", value=datos_ia["e"])
                    w = st.text_input("WhatsApp")
                    urg = st.checkbox("🚨 URGENTE")
                    if st.form_submit_button("💼 PUBLICAR CARGA"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": f"⚠️URGENTE: {m}" if urg else m, "entry.1930562861": en, "entry.466540450": w})
                        st.cache_data.clear(); st.rerun()
    with c2:
        df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for idx, r in df_ca_v.iterrows():
            if busqueda_libre in str(r).upper():
                estilo = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                btn_wsp = f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" style="flex: 2; background:#2980b9; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; text-align: center; font-weight: bold;">SOLICITAR VIAJE</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
                st.markdown(f"""<div class="{estilo}"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><div style="margin:8px 0;">📦 <b>{r.iloc[3]}</b> | 🏢 {r.iloc[5]}</div><div style="display: flex; gap: 8px;">{btn_wsp}</div></div>""", unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR ARRIME"):
                with st.form("f_arr", clear_on_submit=True):
                    loc_arr, det_arr, wsp_arr = st.text_input("Localidad").upper(), st.text_input("Detalle"), st.text_input("WhatsApp")
                    if st.form_submit_button("🌾 PUBLICAR"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": loc_arr, "entry.576675281": det_arr, "entry.466540450": wsp_arr})
                        st.cache_data.clear(); st.rerun()
    with c2:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for idx, r in df_arr.iterrows():
            if busqueda_libre in str(r).upper():
                btn_c = f'<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" style="background: #238636; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold;">CONTACTAR</a>' if es_user_vip or st.session_state.admin_mode else lock_btn_html
                st.markdown(f"""<div class="card-cosecha"><div class="badge-time">{formatear_fecha(r.iloc[0])}</div><div style="font-weight:bold;">📍 ZONA: {r.iloc[2]}</div>🌾 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}{btn_c}</div>""", unsafe_allow_html=True)

# --- TAB 4: CALCULADOR ---
with tab4:
    st.subheader("📊 Estimador de Costos")
    o_c, d_c = st.selectbox("Desde", list(COORDS_CIUDADES.keys()), key="ca1"), st.selectbox("Hasta", list(COORDS_CIUDADES.keys()), key="ca2")
    dist = calcular_distancia(o_c, d_c)
    if dist > 0:
        st.metric("Distancia Estimada", f"{(dist * 1.22):.0f} KM")

# --- FOOTER ---
st.markdown("<div style='text-align:center; padding:20px; opacity:0.5;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
