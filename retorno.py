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
            r = 6371; dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return f"📍 {int(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)))} km aprox."
        return ""
    except: return ""

def validar_cuit(cuit):
    cuit = "".join(filter(str.isdigit, str(cuit)))
    if len(cuit) != 11: return False
    base, aux = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2], 0
    for i in range(10): aux += int(cuit[i]) * base[i]
    aux = 11 - (aux % 11)
    if aux == 11: aux = 0
    if aux == 10: aux = 9
    return aux == int(cuit[10])

# --- 4. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-white, .card-vip, .card-cosecha, .card-bloqueada { transition: all 0.3s ease-in-out; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .card-white { background: white !important; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    .dist-badge { background: #34495e; color: #f1c40f; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold; float: right; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# LOGIN CUIT
with st.container():
    user_cuit = st.text_input("🔑 CUIT de acceso:", "").strip()
    soy_vip_actual = es_vip(user_cuit) if user_cuit and validar_cuit(user_cuit) else False
    if soy_vip_actual: st.success("✅ ACCESO VIP ACTIVO")

# FILTROS
PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

with st.container():
    col1, col2, col3, col4 = st.columns(4)
    b_fecha = col1.date_input("📅 FECHA:", hoy)
    b_o = col2.selectbox("🔍 ORIGEN:", PROVINCIAS)
    b_d = col3.selectbox("🏁 DESTINO:", PROVINCIAS)
    b_e = col4.selectbox("🚛 EQUIPO:", EQUIPOS)
    busqueda_libre = st.text_input("🔎 Búsqueda rápida", "").upper()

# RADAR
cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0
radar_txt = f"🌾 COSECHA ACTIVA: {cant_camiones} Camiones y {cant_cargas} Cargas -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    c_f, c_r = st.columns([1, 2.2])
    with c_f:
        with st.form("f_ca"):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Localidad Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Localidad Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()
    with c_r:
        if not df_ch_raw.empty and len(df_ch_raw.columns) >= 6:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])) and (busqueda_libre in str(r).upper()):
                    val_a, val_b = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                    cuit, wsp = (val_a, val_b) if len(val_a) == 11 else (val_b, val_a)
                    dist = calcular_distancia(r[1], r[2])
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}">{f"<span class=\'dist-badge\'>{dist}</span>" if dist else ""}{"<div class=\'vip-label\'>⭐ CHOFER VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit} | 📱 <b>TEL:</b> {ocultar_telefono(wsp)}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text=Consulta por unidad {r[1]} a {r[2]}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    c_f2, c_r2 = st.columns([1, 2.2])
    with c_f2:
        with st.form("f_ch"):
            op = st.selectbox("Prov. Origen", PROVINCIAS[1:]); ol = st.text_input("Loc. Origen")
            dp = st.selectbox("Prov. Destino", PROVINCIAS[1:]); dl = st.text_input("Loc. Destino")
            et = st.selectbox("Equipo", EQUIPOS[1:]); ci = st.text_input("CUIT/ID"); wn = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                if validar_cuit(ci):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{op} ({ol})", "entry.1519265625": f"{dp} ({dl})", "entry.597193898": et, "entry.1542650763": ci, "entry.1574172378": wn})
                    st.cache_data.clear(); st.rerun()
    with c_r2:
        if not df_ca_raw.empty and len(df_ca_raw.columns) >= 6:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_ca_filtered = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            df_f2 = df_ca_filtered[df_ca_filtered.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-bloqueada">🔒 CARGA EXCLUSIVA VIP<br><small>Disponible en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min</small><br><a href="https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}" target="_blank" style="color:#f1c40f;">⭐ ACTIVAR VIP</a></div>', unsafe_allow_html=True)
                elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}">{"<div class=\'vip-label\'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]} | 📱 <b>TEL:</b> {ocultar_telefono(r[4])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=Consulta carga {r[1]} a {r[2]}" target="_blank" class="btn-wsp">📩 CONSULTAR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    if not df_ca_raw.empty:
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for _, r in df_arrime.iterrows():
            st.markdown(f'<div class="card-cosecha"><div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>{r[3]} | 📱 {ocultar_telefono(r[4])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)
