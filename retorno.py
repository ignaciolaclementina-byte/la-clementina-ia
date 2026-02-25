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

# --- 2. SISTEMA ANTI-PAUSA Y CONTADOR ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

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
ahora = datetime.now()
hoy = ahora.date()

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

# --- 4. ESTILOS VIP PERSONALIZADOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    
    /* BLINDAJE DE TABS: Mas grandes y visibles */
    .stTabs [data-baseweb="tab"] { flex: 1; height: 70px !important; background-color: #1e272e !important; color: white !important; font-size: 20px !important; font-weight: 900 !important; border-radius: 10px 10px 0 0; margin: 0 2px; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border-bottom: 5px solid #f1c40f !important; }

    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 26px; font-weight: 900; color: #f1c40f; display: block; }
    
    /* SEMAFORO DE RECIENCIA */
    .card-hot { background: #fff5f5 !important; border-left: 12px solid #e74c3c !important; }
    .card-medium { background: #f0fff4 !important; border-left: 12px solid #2ecc71 !important; }
    .card-old { background: white !important; border-left: 12px solid #95a5a6 !important; opacity: 0.9; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.4); }

    .card-white, .card-vip, .card-cosecha, .card-bloqueada, .card-hot, .card-medium, .card-old { transition: all 0.3s ease; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-hot:hover, .card-vip:hover { transform: scale(1.02); }
    
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; font-size: 12px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 14px; border-top: 1px solid rgba(255,255,255,0.2); margin-top: 50px; background: rgba(0,0,0,0.5); }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE NEGOCIO ---
def get_card_style(minutos, es_vip_card):
    if es_vip_card: return "card-vip"
    if minutos < 60: return "card-hot"
    if minutos < 180: return "card-medium"
    return "card-old"

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num)))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    val = str(dato).strip().upper().replace(".0", "")
    return val in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Estadísticas
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stats-card"><span class="stats-val">{cant_camiones + cant_cargas}</span>Movimientos Hoy</div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stats-card"><span class="stats-val">{cant_cargas}</span>Cargas Activas</div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span>Socios VIP</div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stats-card"><span class="stats-val">LIVE</span>Sistema Online</div>', unsafe_allow_html=True)

user_cuit = st.text_input("🔑 CUIT de Acceso (Validación automática):", "").strip()
soy_vip_actual = es_vip(user_cuit)
if soy_vip_actual: st.success("🚀 MODO VIP ACTIVADO - Sin esperas")

# Filtros
PROVINCIAS = ["CUALQUIERA"] + sorted(list(COORDS_PROV.keys()))
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

col_b1, col_b2, col_b3, col_b4 = st.columns(4)
b_fecha = col_b1.date_input("📅 Fecha:", hoy)
b_o = col_b2.selectbox("🔍 Origen:", PROVINCIAS)
b_d = col_b3.selectbox("🏁 Destino:", PROVINCIAS)
b_e = col_b4.selectbox("🚛 Equipo:", EQUIPOS)
busqueda = st.text_input("🔎 Filtro rápido (Ciudad, Empresa, Mercadería...)", "").upper()

radar_txt = f"🌾 COSECHA 2026: {cant_camiones} Camiones y {cant_cargas} Cargas disponibles ahora. Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="10">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME COSECHA"])

# --- RENDERIZADO DE TARJETAS ---
with tab1:
    if not df_ch_raw.empty:
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
        for _, r in df_f.iterrows():
            minutos = obtener_minutos_desde_publicacion(r[0])
            is_v = es_vip(r[4]) or es_vip(r[5])
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda in str(r).upper()):
                style = get_card_style(minutos, is_v)
                st.markdown(f'<div class="{style}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>EQUIPO:</b> {r[3]} | <b>TEL:</b> {ocultar_telefono(r[5])}<br><a href="https://wa.me/{limpiar_wsp(r[5])}" class="btn-wsp">✉️ ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME')).any(axis=1)]
        df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
        for _, r in df_f2.iterrows():
            minutos = obtener_minutos_desde_publicacion(r[0])
            is_v = es_vip(r[5])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.markdown(f'<div class="card-bloqueada">🔒 CARGA EXCLUSIVA VIP<br>Disponible en {int(30-minutos)} min</div>', unsafe_allow_html=True)
            elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda in str(r).upper()):
                style = get_card_style(minutos, is_v)
                txt_share = urllib.parse.quote(f"📢 *NUEVA CARGA*\n📍 {r[1]} -> {r[2]}\n📦 {r[3]}\n✅ Retorno Match VIP")
                st.markdown(f'<div class="{style}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 {r[5]}<br><a href="https://wa.me/{limpiar_wsp(r[4])}" class="btn-wsp">📩 CONSULTAR</a><a href="https://wa.me/?text={txt_share}" class="btn-share">📢 DIFUNDIR</a></div>', unsafe_allow_html=True)

with tab3:
    st.info("📍 Sección especializada en viajes de corta distancia (Chacra a Acopio)")
    # (Lógica similar de filtrado para Arrime...)

# --- FOOTER BLINDADO ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 22px; font-weight: bold; color: white; margin-bottom: 5px;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold; letter-spacing: 2px;">© 2026 RETORNO MATCH VIP - LOGÍSTICA INTELIGENTE</p>
    <p style="opacity: 0.6; font-size: 12px;">Desarrollo blindado. Queda prohibida la reproducción parcial o total del código de interfaz sin consentimiento del autor.</p>
</div>
""", unsafe_allow_html=True)
