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

# --- LÓGICA DE MAPA ---
def mostrar_mapa_logistico(df_ch, df_ca):
    puntos = []
    # Camiones en Verde
    for loc in df_ch[df_ch.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].iloc[:, 1].tolist():
        prov = next((p for p in COORDS_PROV if p in str(loc).upper()), None)
        if prov: puntos.append({"lat": COORDS_PROV[prov][0], "lon": COORDS_PROV[prov][1], "color": [0, 255, 128, 160], "tipo": "Camión"})
    # Cargas en Rojo
    for loc in df_ca[df_ca.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].iloc[:, 1].tolist():
        prov = next((p for p in COORDS_PROV if p in str(loc).upper()), None)
        if prov: puntos.append({"lat": COORDS_PROV[prov][0], "lon": COORDS_PROV[prov][1], "color": [255, 71, 87, 160], "tipo": "Carga"})
    
    if puntos:
        df_map = pd.DataFrame(puntos)
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/dark-v10",
            initial_view_state=pdk.ViewState(latitude=-38.416, longitude=-63.616, zoom=3.8, pitch=40),
            layers=[pdk.Layer("ScatterplotLayer", df_map, get_position='[lon, lat]', get_color='color', get_radius=35000)]
        ))

cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP PERSONALIZADOS (IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    
    /* ESTILO DE TABS GRANDES */
    button[data-baseweb="tab"] { font-size: 24px !important; font-weight: bold !important; padding: 15px !important; }
    button[data-baseweb="tab"] p { font-size: 24px !important; }

    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 24px; font-weight: 900; color: #f1c40f; display: block; }
    .card-hot { background: #fff5f5 !important; border-left: 10px solid #e74c3c !important; color: #333; }
    .card-medium { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; color: #777; }
    .card-white, .card-vip, .card-cosecha, .card-bloqueada { transition: all 0.3s ease-in-out; cursor: pointer; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.3); }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; min-height: 220px; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; font-size: 13px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES AUXILIARES (BLINDADAS) ---
def get_card_style(minutos, es_vip_card):
    if es_vip_card: return "card-vip"
    if minutos < 60: return "card-hot"
    if minutos < 180: return "card-medium"
    return "card-old"

def validar_cuit(cuit):
    cuit = "".join(filter(str.isdigit, str(cuit)))
    if len(cuit) != 11: return False
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    aux = sum(int(cuit[i]) * base[i] for i in range(10))
    aux = 11 - (aux % 11)
    if aux == 11: aux = 0
    if aux == 10: aux = 9
    return aux == int(cuit[10])

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

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

with st.container():
    cstats1, cstats2, cstats3, cstats4 = st.columns(4)
    cstats1.markdown(f'<div class="stats-card"><span class="stats-val">{cant_camiones + cant_cargas}</span>Movimientos Hoy</div>', unsafe_allow_html=True)
    cstats2.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span>Miembros VIP</div>', unsafe_allow_html=True)
    cstats3.markdown(f'<div class="stats-card"><span class="stats-val">LIVE</span>Estado Sistema</div>', unsafe_allow_html=True)
    with cstats4: 
        with st.expander("🗺️ MAPA"): mostrar_mapa_logistico(df_ch_raw, df_ca_raw)

user_cuit = st.text_input("🔑 CUIT para acceso VIP:", "").strip()
soy_vip_actual = es_vip(user_cuit)
if soy_vip_actual: st.success("✅ ACCESO VIP ACTIVO")

with st.container():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    b_fecha = c1.date_input("📅 FECHA:", hoy)
    b_o = c2.selectbox("🔍 ORIGEN:", PROVINCIAS)
    b_d = c3.selectbox("🏁 DESTINO:", PROVINCIAS)
    b_e = c4.selectbox("🚛 EQUIPO:", EQUIPOS)
    busqueda_libre = st.text_input("🔎 Búsqueda rápida", "").upper()

radar_txt = f"🌾 COSECHA ACTIVA: {cant_camiones} Camiones y {cant_cargas} Cargas -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: (es_vip(r[4]) or es_vip(r[5])) if len(r) > 5 else False, axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])) and (busqueda_libre in str(r).upper()):
                    minutos = obtener_minutos_desde_publicacion(r[0])
                    card_class = get_card_style(minutos, r['vip'])
                    st.markdown(f'<div class="{card_class}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 EQUIPO:</b> {r[3]} | 📱 <b>TEL:</b> {ocultar_telefono(r[5])}<br><a href="https://wa.me/{limpiar_wsp(r[5])}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            o_p = st.selectbox("Prov. Origen", PROVINCIAS[1:]); o_l = st.text_input("Loc. Origen")
            d_p = st.selectbox("Prov. Destino", PROVINCIAS[1:]); d_l = st.text_input("Loc. Destino")
            et = st.selectbox("Equipo", EQUIPOS[1:]); cid = st.text_input("CUIT"); wnu = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                if validar_cuit(cid):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o_p} ({o_l})", "entry.1519265625": f"{d_p} ({d_l})", "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wnu})
                    st.cache_data.clear(); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip) if len(df_ca_raw.columns) > 5 else False
            df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(30-minutos)} min rest.)</div>', unsafe_allow_html=True)
                elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda_libre in str(r).upper()):
                    txt_w = urllib.parse.quote(f"📢 CARGA: {r[1]} a {r[2]}\n📦 {r[3]}\n✅ Retorno Match VIP")
                    st.markdown(f'<div class="card-medium"><div class="route-txt">{r[1]} ➔ {r[2]}</div>📦 {r[3]} | 🏢 {r[5]}<br><a href="https://wa.me/{limpiar_wsp(r[4])}" class="btn-wsp">📩 CONSULTAR</a><a href="https://wa.me/?text={txt_w}" target="_blank" class="btn-share">📢 DIFUNDIR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for _, r in df_arr.iterrows():
            st.markdown(f'<div class="card-cosecha">🌾 <b>ZONA:</b> {r[2]}<br>{r[3]} | 📱 {ocultar_telefono(r[4])}<br><a href="https://wa.me/{limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="background:#2e7d32">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO - IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        if st.button("LIMPIAR CACHÉ"): st.cache_data.clear(); st.rerun()
