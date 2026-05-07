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

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro Borrado Reforzado
        if not df_ca.empty:
            mask_b = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs = []
            for row in df_ca[mask_b].astype(str).values:
                for cell in row:
                    m = re.search(r'REF:(.*)', cell)
                    if m: refs.append(m.group(1).strip())
            df_ca = df_ca[~mask_b]
            if refs:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs)]

        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    return "549" + (clean[1:] if clean.startswith("0") else clean).replace("15", "", 1) if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos(ts):
    try: return (datetime.now() - pd.to_datetime(ts, dayfirst=True, errors='coerce')).total_seconds() / 60
    except: return 999

def validar_cuit(cuit):
    cuit = "".join(filter(str.isdigit, str(cuit)))
    if len(cuit) != 11: return False
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    aux = sum(int(cuit[i]) * base[i] for i in range(10))
    aux = 11 - (aux % 11)
    if aux == 11: aux = 0
    if aux == 10: aux = 9
    return aux == int(cuit[10])

def calcular_distancia(o, d):
    try:
        o_p = next((p for p in COORDS_PROV if p in str(o).upper()), None)
        d_p = next((p for p in COORDS_PROV if p in str(d).upper()), None)
        if o_p and d_p:
            lat1, lon1 = COORDS_PROV[o_p]; lat2, lon2 = COORDS_PROV[d_p]
            a = math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
            return f"📍 {int(6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))} km"
    except: pass
    return ""

# --- 5. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()
ahora = datetime.now(); hoy = ahora.date()

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; color: white; }
    .card-v { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; }
    .card-vip { background: #fff9e6; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 2px solid #f1c40f; }
    .card-cosecha { background: #e8f5e9; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #2e7d32; }
    .route-txt { font-size: 18px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Login CUIT
with st.container():
    u_cuit = st.text_input("🔑 CUIT de Acceso:", "").strip().replace(".0", "")
    soy_vip = u_cuit in LISTA_VIPS
    if soy_vip: st.success("✅ ACCESO VIP")

# Filtros Globales
c1, c2, c3, c4 = st.columns(4)
b_f = c1.date_input("Fecha:", hoy)
b_o = c2.selectbox("Origen:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
b_d = c3.selectbox("Destino:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
b_s = c4.text_input("Buscar...").upper()

st.markdown(f'<div style="background:red; color:white; padding:10px; border-radius:10px;"><marquee><b>Creado por Ignacio Diaz -- RETORNO MATCH SAN JORGE</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES (Basado en df_ch_raw) ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("f_camion"):
            o = st.selectbox("Origen", list(COORDS_PROV.keys())); d = st.selectbox("Destino", list(COORDS_PROV.keys()))
            e = st.text_input("Equipo"); cu = st.text_input("CUIT"); w = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR CAMIÓN"):
                if validar_cuit(cu):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1542650763": cu, "entry.1574172378": w})
                    st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ch_raw.empty:
            # Filtrado por fecha
            df_v = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))]
            for _, r in df_v.iterrows():
                try:
                    if (b_o == "CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r.iloc[2]).upper()) and (b_s in str(r).upper()):
                        is_v = str(r.iloc[4]) in LISTA_VIPS or str(r.iloc[5]) in LISTA_VIPS
                        st.markdown(f'<div class="{"card-vip" if is_v else "card-v"}"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>EQUIPO:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)
                except: continue

# --- TAB 2: CARGAS (Basado en df_ca_raw) ---
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("f_carga"):
            o = st.selectbox("Origen ", list(COORDS_PROV.keys())); d = st.selectbox("Destino ", list(COORDS_PROV.keys()))
            m = st.text_input("Mercadería"); n = st.text_input("Empresa"); w = st.text_input("WhatsApp ")
            if st.form_submit_button("PUBLICAR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m, "entry.1930562861": n, "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ca_raw.empty:
            df_v = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))]
            # Quitamos los que son Arrime de esta pestaña
            df_v = df_v[~df_v.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for _, r in df_v.iterrows():
                try:
                    mins = obtener_minutos(r.iloc[0])
                    if mins < TIEMPO_EXCLUSIVO_MIN and not soy_vip:
                        st.markdown(f'<div style="background:rgba(0,0,0,0.5); padding:10px; border-radius:10px; text-align:center; border:1px dashed gold;">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-mins)} min)</div>', unsafe_allow_html=True)
                    elif (b_o == "CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r.iloc[2]).upper()) and (b_s in str(r).upper()):
                        st.markdown(f'<div class="card-v"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>CARGA:</b> {r.iloc[3]} | 🏢 {r.iloc[5]}<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)
                except: continue

# --- TAB 3: COSECHA (ARRIME) ---
with tab3:
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("f_arrime"):
            z = st.text_input("📍 Zona"); g = st.text_input("Grano"); w = st.text_input("WhatsApp  ")
            if st.form_submit_button("SUBIR ARRIME"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ca_raw.empty:
            df_a = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                try:
                    st.markdown(f'<div class="card-cosecha"><div class="route-txt">📍 {r.iloc[2]}</div><b>DETALLE:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a></div>', unsafe_allow_html=True)
                    if st.session_state.get("admin_mode", False):
                        if st.button(f"🗑️ BORRAR #{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()
                except: continue

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; margin-top:50px; opacity:0.7;'><hr>Creado por Ignacio Diaz - 2026<br>© RETORNO MATCH VIP</div>", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ ADMIN")
    pin = st.text_input("PIN:", type="password")
    if pin == ADMIN_PIN:
        st.session_state.admin_mode = True
        if st.button("RECARGAR TODO"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False
