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

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS (IGNACIO DIAZ) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        # Cargamos con header=None para evitar KeyError por nombres de columnas cambiantes
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}", header=None).fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}", header=None).fillna("-")
        
        # Blindaje de Borrado
        if not df_ca.empty:
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask_borrado].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        # Carga VIPs
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- 4. FUNCIONES LÓGICAS ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

def obtener_minutos(ts_str):
    try:
        diff = ahora - pd.to_datetime(ts_str, dayfirst=True, errors='coerce')
        return diff.total_seconds() / 60
    except: return 999

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def calcular_distancia(o_str, d_str):
    try:
        o = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o and d:
            lat1, lon1 = COORDS_PROV[o]; lat2, lon2 = COORDS_PROV[d]
            a = math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
            return f"📍 {int(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))} km"
        return ""
    except: return ""

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; border: 1px solid #f1c40f; text-align: center; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-hot { background: white !important; border-left: 10px solid #e74c3c !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; border-radius: 15px; padding: 20px; color: #1b5e20; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; display: inline-block; margin-bottom: 10px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px; border-top: 1px solid rgba(255,255,255,0.1); }
</style>""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- LOGIN Y FILTROS ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
user_cuit = st.text_input("🔑 CUIT VIP:", "").strip()
soy_vip_actual = es_vip(user_cuit)

c1, c2, c3, c4 = st.columns(4)
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
with c3: b_d = st.selectbox("🏁 DESTINO:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
with c4: b_e = st.selectbox("🚛 EQUIPO:", ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea"])

# --- CONTENIDO ---
tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

with tab1:
    if not df_ch_raw.empty:
        # Usamos iloc para evitar KeyError: 0=Timestamp, 1=Origen, 2=Destino, 3=Equipo, 4=CUIT, 5=WSP
        for _, r in df_ch_raw.iterrows():
            if not es_fecha(r.iloc[0], b_fecha): continue
            minutos = obtener_minutos(r.iloc[0])
            is_v = es_vip(r.iloc[4]) or es_vip(r.iloc[5])
            if (b_o=="CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r.iloc[2]).upper()):
                estilo = "card-vip" if is_v else "card-hot"
                st.markdown(f"""<div class="{estilo}">
                    {f'<div class="vip-label">⭐ CHOFER VIP</div>' if is_v else ''}
                    <h3>{r.iloc[1]} ➔ {r.iloc[2]}</h3>
                    <b>Equipo:</b> {r.iloc[3]} | <b>Minutos:</b> {int(minutos)}<br>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">✉️ CONTACTAR</a>
                </div>""", unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if "ARRIME" in str(r).upper() or not es_fecha(r.iloc[0], b_fecha): continue
            minutos = obtener_minutos(r.iloc[0])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.markdown('<div style="color:white; text-align:center; padding:20px; border:1px dashed #f1c40f;">🔒 EXCLUSIVO VIP</div>', unsafe_allow_html=True)
                continue
            st.markdown(f'<div class="card-hot"><h3>{r.iloc[1]} ➔ {r.iloc[2]}</h3><b>Carga:</b> {r.iloc[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">📩 CONSULTAR</a></div>', unsafe_allow_html=True)

with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for idx, r in df_arr.iterrows():
            st.markdown(f'<div class="card-cosecha"><h3>📍 {r.iloc[2]}</h3>{r.iloc[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)
            if st.session_state.admin_mode:
                if st.button(f"🗑️ BORRAR", key=f"del_{idx}"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407":"BORRADO", "entry.576675281":f"REF:{r.iloc[0]}"})
                    st.cache_data.clear(); st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f'<div class="legal-footer"><h3>Creado por Ignacio Diaz</h3><p>© 2026 RETORNO MATCH VIP</p></div>', unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO ADMIN")
