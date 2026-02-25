import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import pydeck as pdk

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30  
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

# --- 4. ESTILOS VIP (IGNACIO DIAZ) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 24px; font-weight: 900; color: #f1c40f; display: block; }
    .card-hot { background: #fff5f5 !important; border-left: 10px solid #e74c3c !important; color: #333; }
    .card-medium { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; color: #777; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; min-height: 200px; border-radius:15px; padding:20px; margin-bottom:15px; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; border-radius:15px; margin-bottom:15px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; font-size: 13px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 5. LÓGICA DE MAPA (MEJORA 3) ---
def generar_mapa(df_ch, df_ca):
    puntos = []
    for d, color in [(df_ch, [0, 255, 128, 160]), (df_ca, [255, 71, 87, 160])]:
        for loc in d.iloc[:, 1].tolist():
            prov = next((p for p in COORDS_PROV if p in str(loc).upper()), None)
            if prov: puntos.append({"lat": COORDS_PROV[prov][0], "lon": COORDS_PROV[prov][1], "color": color})
    
    if puntos:
        df_map = pd.DataFrame(puntos)
        view = pdk.ViewState(latitude=-38.416, longitude=-63.616, zoom=3.5, pitch=40)
        layer = pdk.Layer("ScatterplotLayer", df_map, get_position='[lon, lat]', get_color='color', get_radius=40000, pickable=True)
        st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view, map_style="mapbox://styles/mapbox/dark-v10"))

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Stats y Filtros
cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))])
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))])

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stats-card"><span class="stats-val">{cant_camiones+cant_cargas}</span>Movimientos Hoy</div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span>Socios VIP</div>', unsafe_allow_html=True)
# Mapa en miniatura o expansor
with st.expander("🗺️ VER MAPA DE CALOR EN TIEMPO REAL"):
    generar_mapa(df_ch_raw, df_ca_raw)

# Login CUIT
user_cuit = st.text_input("🔑 CUIT de acceso:", "").strip()
soy_vip_actual = user_cuit in LISTA_VIPS_GLOBAL if user_cuit else False

# Filtros
PROVINCIAS = ["CUALQUIERA"] + list(COORDS_PROV.keys())
f_c1, f_c2, f_c3 = st.columns(3)
b_o = f_c1.selectbox("🔍 ORIGEN:", PROVINCIAS)
b_d = f_c2.selectbox("🏁 DESTINO:", PROVINCIAS)
busqueda = f_c3.text_input("🔎 BUSCAR...", "").upper()

# Radar
radar_txt = f"🌾 COSECHA: {cant_camiones} Camiones y {cant_cargas} Cargas -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee>{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("<h4 style='color:white;'>Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca"):
            eo, ed, ec, en, ew = st.selectbox("Origen", PROVINCIAS[1:]), st.selectbox("Destino", PROVINCIAS[1:]), st.text_input("Carga"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.rerun()
    with col_b:
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda in str(r).upper()):
                minutos = obtener_minutos_desde_publicacion(r[0])
                style = "card-vip" if r[4] in LISTA_VIPS_GLOBAL else ("card-hot" if minutos < 60 else "card-medium")
                st.markdown(f'<div class="{style}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 EQUIPO:</b> {r[3]}<br><a href="https://wa.me/{r[5]}" class="btn-wsp">✉️ CONTACTAR</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS (CON BOTÓN COMPARTIR) ---
with tab2:
    col_a2, col_b2 = st.columns([1, 2])
    with col_b2:
        df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]
        for _, r in df_f2.iterrows():
            if "ARRIME" not in str(r[3]).upper() and (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda in str(r).upper()):
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(30-minutos)} min rest.)</div>', unsafe_allow_html=True)
                else:
                    txt_w = urllib.parse.quote(f"📢 CARGA: {r[1]} a {r[2]}\n📦 {r[3]}\n✅ Retorno Match VIP")
                    st.markdown(f'<div class="card-medium"><div class="route-txt">{r[1]} ➔ {r[2]}</div>📦 {r[3]} | 🏢 {r[5]}<br><a href="https://wa.me/{r[4]}" class="btn-wsp">📩 CONSULTAR</a><a href="https://wa.me/?text={txt_w}" class="btn-share">📢 COMPARTIR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
    for _, r in df_arr.iterrows():
        st.markdown(f'<div class="card-cosecha">🌾 <b>ZONA:</b> {r[2]}<br>{r[3]}<br><a href="https://wa.me/{r[4]}" class="btn-wsp" style="background:#2e7d32">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)

# --- FOOTER (BLINDADO - IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)
