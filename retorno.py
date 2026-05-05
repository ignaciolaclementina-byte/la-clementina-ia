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

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        return (ahora - ts).total_seconds() / 60
    except: return 999

def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = limpiar_dato_numerico(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    val = str(dato).strip().upper().replace(".0", "")
    return val in LISTA_VIPS_GLOBAL

def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return f"📍 {int(6371 * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))} km aprox."
        return ""
    except: return ""

def get_card_style(minutos, es_vip_card):
    if es_vip_card: return "card-vip"
    if minutos < 60: return "card-hot"
    if minutos < 180: return "card-medium"
    return "card-old"

# --- 4. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-hot { background: #fff5f5 !important; border-left: 10px solid #e74c3c !important; color: #333; }
    .card-medium { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; color: #777; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- SISTEMA DE LOGUEO ---
user_cuit = st.sidebar.text_input("🔑 CUIT VIP:", "").strip()
soy_vip_actual = es_vip(user_cuit)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES (CORRECCIÓN ILOC AQUÍ) ---
with tab1:
    if not df_ch_raw.empty:
        # CORRECCIÓN DEFINITIVA DE LA LÍNEA 245
        df_ch_raw['vip'] = df_ch_raw.apply(lambda r: (es_vip(r.iloc[4]) or es_vip(r.iloc[5])) if len(r) > 5 else False, axis=1)
        
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].sort_values(by='vip', ascending=False)
        for _, r in df_f.iterrows():
            minutos = obtener_minutos_desde_publicacion(r.iloc[0])
            card_class = get_card_style(minutos, r['vip'])
            st.markdown(f'<div class="{card_class} card-vip">{"<div class=\'vip-label\'>⭐ CHOFER VIP</div>" if r["vip"] else ""}<div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>EQUIPO:</b> {r.iloc[3]} | <b>TEL:</b> {ocultar_telefono(r.iloc[5])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip) if len(df_ca_raw.columns) > 5 else False
        df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].sort_values(by='vip', ascending=False)
        for _, r in df_f2.iterrows():
            minutos = obtener_minutos_desde_publicacion(r.iloc[0])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)} min rest.)</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="card-white card-vip" style="background:white; padding:15px; border-radius:10px; margin-bottom:10px;"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>CARGA:</b> {r.iloc[3]} | <b>EMPRESA:</b> {r.iloc[5]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    if not df_ca_raw.empty:
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for _, r in df_arrime.iterrows():
            st.markdown(f'<div class="card-cosecha" style="padding:15px; border-radius:10px; margin-bottom:10px;"><div class="route-txt">📍 {r.iloc[2]}</div>{r.iloc[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a></div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""<div class="legal-footer"><p>Creado por Ignacio Diaz © 2026</p></div>""", unsafe_allow_html=True)
