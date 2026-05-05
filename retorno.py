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
WSP_VENTAS_VIP = "5493401525621"

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

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- 4. FUNCIONES DE LÓGICA ---
def es_fecha(f, target):
    try:
        return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            r = 6371 
            dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return f"📍 {int(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))} km"
        return ""
    except: return ""

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #f1c40f; text-align: center; font-weight: bold; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-hot { background: white !important; border-left: 10px solid #e74c3c !important; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-bloqueada { background: rgba(0,0,0,0.7) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px; border-radius: 15px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.8); padding: 40px; border-top: 1px solid #f1c40f; margin-top: 50px; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 12px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- LOGIN CUIT ---
if 'soy_vip' not in st.session_state: st.session_state.soy_vip = False
user_cuit = st.text_input("🔑 Ingrese su CUIT para acceso completo:", "").strip()
st.session_state.soy_vip = es_vip(user_cuit)

if st.session_state.soy_vip:
    st.success("✅ MODO VIP ACTIVADO")

# --- FILTROS ---
PROVINCIAS = ["CUALQUIERA"] + sorted(list(COORDS_PROV.keys()))
c1, c2, c3 = st.columns(3)
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_f = st.date_input("📅 FECHA:", hoy)

# --- RADAR ---
radar_txt = f"SISTEMA ACTIVO -- Creado por Ignacio Diaz -- {len(df_ca_raw)} Cargas disponibles."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- LÓGICA DE CARDS ---
with tab1: # Camiones
    if not df_ch_raw.empty:
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))]
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                st.markdown(f'<div class="card-hot"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>Equipo:</b> {r[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}" class="btn-wsp">CONTACTAR CHOFER</a></div>', unsafe_allow_html=True)

with tab2: # Cargas
    if not df_ca_raw.empty:
        df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))]
        for _, r in df_f2.iterrows():
            minutos = obtener_minutos_desde_publicacion(r[0])
            es_vip_carga = es_vip(r[5])
            
            if minutos < TIEMPO_EXCLUSIVO_MIN and not st.session_state.soy_vip:
                st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)} min rest.)</div>', unsafe_allow_html=True)
            elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                clase = "card-vip" if es_vip_carga else "card-hot"
                dist = calcular_distancia(r[1], r[2])
                st.markdown(f'<div class="{clase}"><span style="float:right">{dist}</span>{"<div class=\'vip-label\'>⭐ VIP</div>" if es_vip_carga else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>Carga:</b> {r[3]} | <b>Empresa:</b> {r[5]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">SOLICITAR CARGA</a></div>', unsafe_allow_html=True)

with tab3: # Arrime
    st.info("Sección de arrime de cosecha directa.")
    df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
    for _, r in df_arrime.iterrows():
        st.markdown(f'<div class="card-cosecha"><div class="route-txt">🌾 {r[2]}</div>{r[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp" style="background:#2e7d32">CONTACTAR</a></div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 22px; font-weight: bold; color: #f1c40f;">Creado por Ignacio Diaz</p>
    <p>© 2026 | San Jorge, Santa Fe | Todos los derechos reservados</p>
</div>
""", unsafe_allow_html=True)
