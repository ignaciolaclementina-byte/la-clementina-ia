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
WSP_VENTAS_VIP = "5493401525621" # Tu contacto para nuevos clientes VIP

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

# --- 2. SISTEMA ANTI-PAUSA Y CONTADOR ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

if "visitas" not in st.session_state:
    st.session_state.visitas = 1

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=10)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now(); hoy = ahora.date()

# --- FUNCIONES AUXILIARES ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0","")))
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0","")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

# --- 5. ESTILOS Y INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown(f"""
<style>
    .stApp {{ background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }}
    .radar-container {{ background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; text-align: center; border: 1px solid #f1c40f; }}
    .card-white, .card-vip {{ border-radius: 15px; padding: 20px; margin-bottom: 15px; background: white; border-left: 10px solid #3498db; color: #333; }}
    .card-vip {{ background: #fff9e6; border: 3px solid #f1c40f; }}
    .route-txt {{ font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }}
    .legal-footer {{ text-align: center; color: white; padding: 50px; opacity: 0.7; }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

user_cuit = st.text_input("🔑 Ingrese su CUIT:", "").strip()
soy_vip_actual = es_vip(user_cuit)

PROVINCIAS = ["CUALQUIERA"] + list(COORDS_PROV.keys())
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

c1, c2, c3, c4 = st.columns(4)
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">Creado por Ignacio Diaz -- Cosecha Activa 2026</marquee></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS"])

# --- TAB 1: CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()):
                st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>EQUIPO:</b> {r[3]}</div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
        df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f2.iterrows():
            minutos = obtener_minutos_desde_publicacion(r[0])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.write("🔒 Carga Exclusiva VIP")
            elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()):
                st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>CARGA:</b> {r[3]} | 🏢 {r[5]}</div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold;">Creado por Ignacio Diaz</p>
    <p>© 2026 RETORNO MATCH VIP</p>
</div>
""", unsafe_allow_html=True)
