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
WSP_VENTAS_VIP = "5493401525621" # Contacto para nuevos VIP

# --- COORDENADAS PARA GEOLOCALIZACIÓN (IGNACIO DIAZ) ---
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

# --- 3. CARGA DE DATOS SEGUROS CON FILTRO DE BORRADO POTENCIADO ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # --- BLINDAJE DE BORRADO MEJORADO (Ignacio Diaz) ---
        if not df_ca.empty:
            # Identificamos instrucciones de borrado por palabra clave en columnas específicas
            mask_borrado = (df_ca.iloc[:, 0].astype(str).str.upper() == 'BORRADO') | \
                           (df_ca.iloc[:, 1].astype(str).str.upper() == 'BORRADO')
            
            # Extraemos los IDs de las cargas que deben desaparecer
            refs_para_quitar = []
            filas_instruccion = df_ca[mask_borrado]
            for _, f in filas_instruccion.iterrows():
                match = re.search(r'REF:(.*)', str(f.iloc[2]))
                if match:
                    refs_para_quitar.append(match.group(1).strip())
            
            # Aplicamos el filtro doble
            df_ca = df_ca[~mask_borrado] # Quitamos la "orden" de borrar
            if refs_para_quitar:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_para_quitar)] # Quitamos la carga original
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

ahora = datetime.now()
hoy = ahora.date()

# --- FUNCIONES DE FECHA Y TIEMPO ---
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

# --- VARIABLES DE ESTADO ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP (IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 24px; font-weight: 900; color: #f1c40f; display: block; }
    .stats-label { font-size: 12px; text-transform: uppercase; opacity: 0.8; }
    .card-hot { background: #fff5f5 !important; border-left: 10px solid #e74c3c !important; color: #333; }
    .card-medium { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; color: #777; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 25px; border-radius: 15px; }
    .route-txt { font-size: 19px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 8px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 50px; background-color: #2c3e50 !important; color: white !important; font-weight: 900 !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE NEGOCIO ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Estadísticas Rápidas
with st.container():
    cs1, cs2, cs3, cs4 = st.columns(4)
    with cs1: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(df_ch_raw)+len(df_ca_raw)}</span><span class="stats-label">Total Movimientos</span></div>', unsafe_allow_html=True)
    with cs2: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span><span class="stats-label">Miembros VIP</span></div>', unsafe_allow_html=True)
    with cs3: st.markdown(f'<div class="stats-card"><span class="stats-val">ACTIVO</span><span class="stats-label">Sincronización</span></div>', unsafe_allow_html=True)
    with cs4: st.markdown(f'<div class="stats-card"><span class="stats-val">2026</span><span class="stats-label">Versión</span></div>', unsafe_allow_html=True)

# Login CUIT
with st.container():
    user_cuit = st.text_input("🔑 CUIT para acceso VIP:", "").strip()
    soy_vip_actual = es_vip(user_cuit)
    if soy_vip_actual: st.success("✅ ACCESO VIP ACTIVO")

# Filtros Globales
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1: b_fecha = st.date_input("📅 Fecha:", hoy)
    with c2: b_o = st.selectbox("🔍 Origen:", PROVINCIAS)
    with c3: b_d = st.selectbox("🏁 Destino:", PROVINCIAS)
    with c4: b_e = st.selectbox("🚛 Equipo:", EQUIPOS)
    busqueda_libre = st.text_input("🔎 Búsqueda rápida:", "").upper()

st.markdown(f'<div class="radar-container"><marquee scrollamount="7">{st.session_state.anuncios} -- Creado por Ignacio Diaz.</marquee></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with t1:
    col_f, col_r = st.columns([1, 2.2])
    with col_f:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo, elo = st.selectbox("Origen", PROVINCIAS[1:]), st.text_input("Localidad")
            ed, eld = st.selectbox("Destino", PROVINCIAS[1:]), st.text_input("Localidad ")
            ec, en, ew = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()
    with col_r:
        if not df_ch_raw.empty:
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                    link = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Consulta unidad {r[1]} a {r[2]}"
                    st.markdown(f'<div class="card-old"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 {r[3]}</b> | 📱 {ocultar_telefono(r[5])}<br><a href="{link}" target="_blank" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            op, ol = st.selectbox("Origen", PROVINCIAS[1:]), st.text_input("Localidad")
            dp, dl = st.selectbox("Destino", PROVINCIAS[1:]), st.text_input("Localidad ")
            et, cid, wn = st.selectbox("Equipo", EQUIPOS[1:]), st.text_input("CUIT"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{op} ({ol})", "entry.1519265625": f"{dp} ({dl})", "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wn})
                st.cache_data.clear(); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)}m restantes)</div>', unsafe_allow_html=True)
                elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                    link = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=Consulta carga {r[1]} a {r[2]}"
                    st.markdown(f'<div class="card-medium"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 {r[3]}</b> | 🏢 {r[5]}<br><a href="{link}" target="_blank" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA (ARRIME) ---
with t3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 ARRIME DE COSECHA</h3>", unsafe_allow_html=True)
    ca1, ca2 = st.columns([1, 2.2])
    with ca1:
        with st.form("f_arr", clear_on_submit=True):
            zl = st.text_input("📍 Zona"); gd = st.text_input("🌾 Grano/Detalle"); tv = st.text_input("💰 Tarifa"); wa = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                # Se publica con "ARRIME" para que el filtro lo reconozca
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": zl, "entry.576675281": f"ARRIME|{gd}|{tv}", "entry.1930562861": "COSECHA", "entry.466540450": wa})
                st.cache_data.clear(); st.rerun()
    with ca2:
        if not df_ca_raw.empty:
            df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for i, (idx, r) in enumerate(df_arr.iterrows()):
                st.markdown(f'<div class="card-cosecha"><div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>{r[3]} | 📱 {ocultar_telefono(r[4])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">CONTACTAR</a></div>', unsafe_allow_html=True)
                if st.session_state.get('admin_mode', False):
                    if st.button(f"🗑️ BORRAR #{i}", key=f"del_{idx}"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.170847116": "BORRADO", "entry.576675281": f"REF:{r[0]}", "entry.1930562861": "SISTEMA", "entry.466540450": "0"})
                        st.cache_data.clear(); st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("Radar:", st.session_state.anuncios)
        if st.button("RESET"): st.cache_data.clear(); st.rerun()
