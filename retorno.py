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

# --- MEJORA: LIMPIEZA DE DATOS VIEJOS (Ignacio Diaz) ---
def filtrar_recientes(df):
    if df.empty: return df
    try:
        # Solo mostrar publicaciones de hoy y ayer para mantener la base fresca
        hace_24h = ahora - timedelta(hours=24)
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df[df.iloc[:, 0] >= hace_24h]
    except: return df

df_ch_raw = filtrar_recientes(df_ch_raw)
df_ca_raw = filtrar_recientes(df_ca_raw)

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

PROVINCIAS = ["CUALQUIERA"] + sorted(list(COORDS_PROV.keys()))
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP PERSONALIZADOS (IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-white, .card-vip, .card-cosecha, .card-bloqueada { transition: all 0.3s ease-in-out; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .card-white { background: white !important; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.3); }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-wsp:hover { background-color: #128C7E; transform: scale(1.02); }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES AUXILIARES (IGNACIO DIAZ) ---
def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            r = 6371 
            dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return f"📍 {int(r * c)} km"
        return ""
    except: return ""

# MEJORA: Validación robusta de WhatsApp
def validar_whatsapp(num):
    num = "".join(filter(str.isdigit, str(num)))
    return len(num) >= 10

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_dato(dato, es_vip_user):
    if es_vip_user: return dato
    d = str(dato)
    return f"{d[:2]}***{d[-3:]}" if len(d) > 5 else "***"

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Login y CUIT
with st.container():
    c_log1, c_log2 = st.columns([2, 1])
    with c_log1:
        user_cuit = st.text_input("🔑 ACCESO: Ingrese su CUIT (Empresa o Chofer):", "").strip()
        soy_vip_actual = es_vip(user_cuit) if user_cuit else False
        if soy_vip_actual: st.success("✅ MODO VIP ACTIVADO")

# Filtros
with st.container():
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
    with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
    with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
    with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
    with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
    
    col_bus, col_res = st.columns([3, 1])
    with col_bus:
        busqueda_libre = st.text_input("🔎 Búsqueda rápida (Ciudad, Empresa, etc.)", "").upper()
    with col_res:
        if st.button("🔄 REINICIAR FILTROS"):
            st.rerun()

# Radar
cant_camiones = len(df_ch_raw) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw) if not df_ca_raw.empty else 0
radar_txt = f"🔥 ACTIVIDAD EN TIEMPO REAL: {cant_camiones} Camiones y {cant_cargas} Cargas disponibles -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee>{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Ciudad Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Ciudad Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("🚀 PUBLICAR"):
                if validar_whatsapp(ew):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                    st.toast("Carga publicada correctamente", icon="✅")
                    time.sleep(1); st.cache_data.clear(); st.rerun()
                else: st.error("WhatsApp inválido")

    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: (es_vip(r[4]) or es_vip(r[5])) if len(r) > 5 else False, axis=1)
            df_f = df_ch_raw.sort_values(by='vip', ascending=False)
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])) and (busqueda_libre in str(r).upper()):
                    dist = calcular_distancia(r[1], r[2])
                    wsp = r[5] if len(str(r[4])) == 11 else r[4]
                    msg = urllib.parse.quote(f"Hola! Vi tu camión en RETORNO MATCH VIP para {r[1]} -> {r[2]}. Me interesa.")
                    link = f"https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text={msg}"
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><b>{r[1]} ➔ {r[2]}</b> <small style="float:right">{dist}</small><br>🚛 {r[3]} | 🆔 {ocultar_dato(r[4], soy_vip_actual)}<br><a href="{link}" target="_blank" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS (Con Bloqueo VIP de 30 min) ---
with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            op = st.selectbox("Prov. Origen", PROVINCIAS[1:]); ol = st.text_input("Ciudad Origen")
            dp = st.selectbox("Prov. Destino", PROVINCIAS[1:]); dl = st.text_input("Ciudad Destino")
            et = st.selectbox("Equipo", EQUIPOS[1:]); cid = st.text_input("CUIT"); wn = st.text_input("WhatsApp")
            if st.form_submit_button("🚀 PUBLICAR"):
                if len(cid) >= 11 and validar_whatsapp(wn):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{op} ({ol})", "entry.1519265625": f"{dp} ({dl})", "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wn})
                    st.toast("Camión publicado!", icon="✅")
                    time.sleep(1); st.cache_data.clear(); st.rerun()
                else: st.error("Revise CUIT y WhatsApp")

    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            for _, r in df_ca_raw.iterrows():
                if "ARRIME" in str(r[3]).upper(): continue
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP<br><small>Disponible para todos en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min</small><br><a href="https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}" style="color:#f1c40f;">⭐ HACERME VIP</a></div>', unsafe_allow_html=True)
                elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                    msg_ca = urllib.parse.quote(f"Hola {r[5]}, vi tu carga {r[3]} en RETORNO MATCH VIP. Tengo camión.")
                    link_ca = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_ca}"
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><b>{r[1]} ➔ {r[2]}</b><br>📦 {r[3]} | 🏢 {r[5]}<br><a href="{link_ca}" target="_blank" class="btn-wsp">CONSULTAR CARGA</a></div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 ARRIME Y COSECHA</h3>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        with st.form("f_arr", clear_on_submit=True):
            zl = st.text_input("📍 Zona/Localidad"); gd = st.text_input("🌾 Cereal/Detalle"); tv = st.text_input("💰 Tarifa"); wa = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": zl, "entry.576675281": f"ARRIME|{gd}|{tv}", "entry.1930562861": "COSECHA", "entry.466540450": wa})
                st.cache_data.clear(); st.rerun()
    with col_a2:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for _, r in df_arr.iterrows():
            st.markdown(f'<div class="card-cosecha"><b>📍 ZONA: {r[2]}</b><br>{r[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="background:#2e7d32">CONTACTAR</a></div>', unsafe_allow_html=True)

# --- PIE DE PÁGINA (IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <h3 style="color:white;">Creado por Ignacio Diaz</h3>
    <p style="color:#f1c40f;">© 2026 RETORNO MATCH VIP - San Jorge, Santa Fe</p>
    <p>Software de logística blindado. Prohibida su reproducción.</p>
</div>
""", unsafe_allow_html=True)
