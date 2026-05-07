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
TIEMPO_EXCLUSIVO_MIN = 30  # Ventaja competitiva para usuarios VIP
WSP_VENTAS_VIP = "5493401525621" # Contacto comercial

# --- COORDENADAS PARA GEOLOCALIZACIÓN ---
COORDS_PROV = {
    "BUENOS AIRES": (-34.921, -57.954), "CABA": (-34.603, -58.381), "CATAMARCA": (-28.469, -65.785),
    "CHACO": (-27.451, -58.986), "CHUBUT": (-43.300, -65.102), "CORDOBA": (-31.413, -64.181),
    "CORRIENTES": (-27.469, -58.830), "ENTRE RIOS": (-31.733, -60.529), "FORMOSA": (-26.177, -58.178),
    "JUJUY": (-24.185, -65.299), "LA PAMPA": (-36.616, -64.283), "LA RIOJA": (-29.411, -66.850),
    "MENDOZA": (-32.889, -68.845), "MISIONES": (-27.367, -55.896), "NEUQUEN": (-38.951, -68.059),
    "RIO NEGRO": (-40.813, -62.996), "SALTA": (-24.785, -65.411), "SAN JUAN": (-31.537, -68.536),
    "SAN LUIS": (-33.295, -66.335), "SANTA CRUZ": (-51.622, -69.218), "SANTA FE": (-31.633, -60.700),
    "SANTIAGO DEL ESTERO": (-27.795, -64.263), "TIERRA DEL FUEGO": (-54.801, -68.303), "TUCUMAN": (-26.824, -65.222)
}

# --- 2. CARGA DE DATOS CON BLINDAJE ANTI-ERROR (KeyError Proof) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        # Carga con .fillna para evitar errores de tipo
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Inteligente
        if not df_ca.empty:
            # Identificar filas marcadas como BORRADO
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            # Extraer referencias REF:timestamp
            refs_borradas = []
            for val in df_ca[mask_borrado].astype(str).values.flatten():
                match = re.search(r'REF:(.*)', val)
                if match: refs_borradas.append(match.group(1).strip())
            
            # Limpiar el dataframe: quitamos los avisos de borrado y las cargas referenciadas
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        # Lista VIP
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de sincronización: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

# --- 3. FUNCIONES DE LÓGICA Y FORMATO ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos(timestamp_str):
    try:
        diff = datetime.now() - pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        return diff.total_seconds() / 60
    except: return 999

def calcular_distancia(o, d):
    try:
        o_p = next((p for p in COORDS_PROV if p in str(o).upper()), None)
        d_p = next((p for p in COORDS_PROV if p in str(d).upper()), None)
        if o_p and d_p:
            lat1, lon1 = COORDS_PROV[o_p]; lat2, lon2 = COORDS_PROV[d_p]
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi, dlam = math.radians(lat2-lat1), math.radians(lon2-lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
            return f"📍 {int(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))} km"
    except: pass
    return ""

# --- 4. CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0e1117; color: white; }
    .card-white { background: white; color: #333; padding: 20px; border-radius: 15px; border-left: 10px solid #3498db; margin-bottom: 15px; }
    .card-vip { background: #fff9e6; color: #333; padding: 20px; border-radius: 15px; border: 2px solid #f1c40f; margin-bottom: 15px; }
    .card-cosecha { background: #e8f5e9; color: #1b5e20; padding: 20px; border-radius: 15px; border-left: 10px solid #2e7d32; margin-bottom: 15px; }
    .card-hot { border-left: 10px solid #e74c3c !important; }
    .card-bloqueada { background: #1a1c23; border: 2px dashed #f1c40f; padding: 25px; border-radius: 15px; text-align: center; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
    .vip-badge { background: #f1c40f; color: black; padding: 3px 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN ---
df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'radar' not in st.session_state: st.session_state.radar = "¡Bienvenido a Retorno Match VIP!"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]

# --- 5. CUERPO DE LA APP ---
st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

with st.expander("🔑 ACCESO VIP / LOGIN"):
    user_cuit = st.text_input("Ingrese CUIT/ID:", "").strip().replace(".0", "")
    soy_vip = user_cuit in LISTA_VIPS
    if soy_vip: st.success("✅ MODO VIP ACTIVADO")

# Filtros
c1, c2, c3, c4 = st.columns(4)
f_fecha = c1.date_input("Día:", hoy)
f_orig = c2.selectbox("Origen:", PROVINCIAS)
f_dest = c3.selectbox("Destino:", PROVINCIAS)
f_search = c4.text_input("Buscador libre:").upper()

st.markdown(f'<div style="background:#e74c3c; color:white; padding:10px; border-radius:10px; text-align:center;"><marquee><b>{st.session_state.radar} -- Creado por Ignacio Diaz</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Publicar Carga")
        with st.form("p_carga", clear_on_submit=True):
            o = st.selectbox("Origen", PROVINCIAS[1:]); d = st.selectbox("Destino", PROVINCIAS[1:])
            m = st.text_input("Mercadería"); e = st.text_input("Empresa"); w = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m, "entry.1930562861": e, "entry.466540450": w})
                st.cache_data.clear(); st.rerun()

    with col2:
        if not df_ch_raw.empty:
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, f_fecha))]
            for _, r in df_f.iterrows():
                if len(r) < 6: continue
                # Filtrado lógico
                if (f_orig == "CUALQUIERA" or f_orig in str(r[1]).upper()) and (f_dest == "CUALQUIERA" or f_dest in str(r[2]).upper()) and (f_search in str(r).upper()):
                    es_v = str(r[4]) in LISTA_VIPS or str(r[5]) in LISTA_VIPS
                    minutos = obtener_minutos(r[0])
                    dist = calcular_distancia(r[1], r[2])
                    clase = "card-vip" if es_v else ("card-white card-hot" if minutos < 60 else "card-white")
                    
                    st.markdown(f"""
                    <div class="{clase}">
                        <span style="float:right; font-weight:bold; color:#777;">{dist}</span>
                        {f'<span class="vip-badge">⭐ VIP</span>' if es_v else ''}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>EQUIPO:</b> {r[3]} | 📱 <b>TEL:</b> {ocultar_telefono(r[5])}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Hola!" class="btn-wsp">CONTACTAR</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Publicar Camión")
        with st.form("p_camion", clear_on_submit=True):
            o = st.selectbox("Desde", PROVINCIAS[1:]); d = st.selectbox("Hacia", PROVINCIAS[1:])
            eq = st.text_input("Equipo"); cu = st.text_input("CUIT"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": w})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ca_raw.empty:
            df_f = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, f_fecha))]
            df_f = df_f[~df_f.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for _, r in df_f.iterrows():
                if len(r) < 6: continue
                minutos = obtener_minutos(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip:
                    st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)} min rest.)</div>', unsafe_allow_html=True)
                elif (f_orig == "CUALQUIERA" or f_orig in str(r[1]).upper()) and (f_dest == "CUALQUIERA" or f_dest in str(r[2]).upper()) and (f_search in str(r).upper()):
                    st.markdown(f"""
                    <div class="card-white">
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>CARGA:</b> {r[3]} | 🏢 {r[5]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">CONSULTAR</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 3: COSECHA (CON BORRADO SEGURO) ---
with tab3:
    st.markdown("<h3 style='text-align:center;'>🌾 SECCIÓN ARRIME</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("p_arrime"):
            z = st.text_input("📍 Zona"); g = st.text_input("Detalle"); w = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR ARRIME"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with col2:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME|COSECHA', case=False)).any(axis=1)]
        for idx, r in df_arr.iterrows():
            if len(r) < 5: continue
            st.markdown(f"""
            <div class="card-cosecha">
                <div class="route-txt">📍 {r[1]}</div>
                <b>DETALLE:</b> {r[2]} | 📱 {ocultar_telefono(r[4])}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)
            if st.session_state.admin_mode:
                if st.button(f"🗑️ BORRAR #{idx}"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r[0]}"})
                    st.cache_data.clear(); st.rerun()

# --- 6. FOOTER ---
st.markdown(f"""
<div style="text-align:center; padding:50px; opacity:0.6;">
    <hr>
    <p>Creado por Ignacio Diaz</p>
    <p>© 2026 RETORNO MATCH VIP - Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ ADMIN")
    pin = st.text_input("PIN:", type="password")
    if pin == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.radar = st.text_area("Mensaje Radar:", st.session_state.radar)
        if st.button("LIMPIAR TODO"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False
