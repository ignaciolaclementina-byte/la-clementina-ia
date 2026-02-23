import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE PRIMERO) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚚", layout="wide")

import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 2. CONSTANTES Y ESTRUCTURA (IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

# URLs de Google Forms (Respuestas)
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323"
PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

# --- 3. ESTILOS CSS PROFESIONALES ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 2px solid #f1c40f; text-align: center; }
    
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.4); border-left: 10px solid #f1c40f; position: relative; }
    
    .badge-nuevo { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; position: absolute; top: 10px; right: 10px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }
    
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 13px; display: inline-block; margin-bottom: 8px; }
    .route-txt { font-size: 19px; font-weight: 900; color: #1e3799; text-transform: uppercase; margin-bottom: 5px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; border: none; }
    
    .share-btn { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-decoration: none; font-size: 30px; }
</style>
<a href="https://api.whatsapp.com/send?text=¡Encontré esta App de Retornos! 🚚 https://retorno-match-sanjorge.streamlit.app" class="share-btn" target="_blank">📲</a>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES DE PROTECCIÓN ---
def safe_str(val):
    """Convierte cualquier valor a string limpio para evitar errores de tipo."""
    if pd.isna(val): return ""
    return str(val).replace(".0", "").strip()

def sanitizar_numero(dato):
    """Extrae solo números para CUIT o Teléfono."""
    s = safe_str(dato)
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    """Formatea el número para link de WhatsApp."""
    clean = sanitizar_numero(num)
    if not clean or len(clean) < 7: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def check_fecha(val_fecha, target_fecha):
    """Compara fechas de forma segura."""
    try:
        if not val_fecha or val_fecha == "-": return False
        return pd.to_datetime(val_fecha, dayfirst=True).date() == target_fecha
    except: return False

def check_nuevo(val_ts):
    """Verifica si el registro tiene menos de 3 horas."""
    try:
        ts = pd.to_datetime(val_ts, dayfirst=True)
        return (datetime.now() - ts) < timedelta(hours=3)
    except: return False

@st.cache_data(ttl=15)
def fetch_data():
    """Carga datos con manejo de errores de conexión."""
    try:
        t = int(time.time())
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        v_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [safe_str(x).upper() for x in v_raw[0].dropna().tolist()]
        return ch, ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 5. INICIO DE APLICACIÓN ---
with st.spinner("Sincronizando con base de datos de Ignacio Diaz..."):
    df_ch_raw, df_ca_raw, LISTA_VIPS = fetch_data()

if 'anuncios' not in st.session_state: st.session_state.anuncios = "¡Bienvenido al sistema VIP!"
hoy = datetime.now().date()

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Filtros
c1, c2, c3, c4 = st.columns(4)
with c1: f_busqueda = st.date_input("📅 FECHA:", hoy)
with c2: o_busqueda = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: d_busqueda = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: e_busqueda = st.selectbox("🚛 EQUIPO:", EQUIPOS)

q_busqueda = st.text_input("📍 BUSCADOR GLOBAL (Ciudad, Empresa, Carga...)", placeholder="Ej: San Jorge, Sider, Arcor...").upper()

# Radar
ch_hoy = len(df_ch_raw[df_ch_raw.iloc[:,0].apply(lambda x: check_fecha(x, hoy))]) if not df_ch_raw.empty else 0
ca_hoy = len(df_ca_raw[df_ca_raw.iloc[:,0].apply(lambda x: check_fecha(x, hoy))]) if not df_ca_raw.empty else 0
radar_html = f"🔥 HOY: {ch_hoy} Camiones y {ca_hoy} Cargas -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz"
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_html}</marquee></div>', unsafe_allow_html=True)

tab_ch, tab_ca = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS DISPONIBLES"])

# --- TAB 1: VER CAMIONES ---
with tab_ch:
    col_izq, col_der = st.columns([1, 2.2])
    with col_izq:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f1", clear_on_submit=True):
            f_o = st.selectbox("Origen", PROVINCIAS[1:]); f_lo = st.text_input("Localidad")
            f_d = st.selectbox("Destino", PROVINCIAS[1:]); f_ld = st.text_input("Localidad")
            f_c = st.text_input("Mercadería"); f_e = st.text_input("Empresa"); f_w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{f_o} ({f_lo})", "entry.170847116": f"{f_d} ({f_ld})", "entry.576675281": f_c, "entry.1930562861": f_e, "entry.466540450": sanitizar_numero(f_w)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_der:
        if not df_ch_raw.empty:
            df_ch_raw['is_vip'] = df_ch_raw.apply(lambda r: safe_str(r[4]).upper() in LISTA_VIPS or safe_str(r[5]).upper() in LISTA_VIPS, axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:,0].apply(lambda x: check_fecha(x, f_busqueda))].sort_values(by='is_vip', ascending=False)
            
            for _, r in df_f.iterrows():
                try:
                    txt_full = f"{r[1]} {r[2]} {r[3]} {r[4]} {r[5]}".upper()
                    if (o_busqueda=="CUALQUIERA" or o_busqueda in safe_str(r[1]).upper()) and \
                       (d_busqueda=="CUALQUIERA" or d_busqueda in safe_str(r[2]).upper()) and \
                       (e_busqueda=="CUALQUIERA" or e_busqueda == safe_str(r[3])) and \
                       (q_busqueda in txt_full):
                        
                        id_v = sanitizar_numero(r[4]) if len(sanitizar_numero(r[4])) > 9 else sanitizar_numero(r[5])
                        tel_v = sanitizar_numero(r[5]) if id_v != sanitizar_numero(r[5]) else sanitizar_numero(r[4])
                        
                        nuevo_b = '<div class="badge-nuevo">NUEVO</div>' if check_nuevo(r[0]) else ''
                        w_msg = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n✅ *INTERÉS EN UNIDAD*\n📍 RUTA: {r[1]} -> {r[2]}\n🚛 EQUIPO: {r[3]}\n\n¿Sigue disponible?")
                        
                        st.markdown(f'''<div class="{"card-vip" if r["is_vip"] else "card-white"}">{nuevo_b}
                        {"<div class='vip-label'>⭐ CHOFER VIP</div>" if r["is_vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>EQUIPO:</b> {r[3]} | 🆔 <b>ID:</b> {id_v}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(tel_v)}&text={w_msg}" target="_blank" class="btn-wsp">✉️ CONTACTAR CHOFER</a></div>''', unsafe_allow_html=True)
                except: continue

# --- TAB 2: VER CARGAS ---
with tab_ca:
    col_izq2, col_der2 = st.columns([1, 2.2])
    with col_izq2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f2", clear_on_submit=True):
            p_o = st.selectbox("Origen", PROVINCIAS[1:]); p_lo = st.text_input("Localidad")
            p_d = st.selectbox("Destino", PROVINCIAS[1:]); p_ld = st.text_input("Localidad")
            p_e = st.selectbox("Equipo", EQUIPOS[1:]); p_id = st.text_input("CUIT/ID"); p_w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{p_o} ({p_lo})", "entry.1519265625": f"{p_d} ({p_ld})", "entry.597193898": p_e, "entry.1542650763": sanitizar_numero(p_id), "entry.1574172378": sanitizar_numero(p_w)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_der2:
        if not df_ca_raw.empty:
            df_ca_raw['is_vip'] = df_ca_raw.iloc[:,5].apply(lambda x: safe_str(x).upper() in LISTA_VIPS)
            df_f2 = df_ca_raw[df_ca_raw.iloc[:,0].apply(lambda x: check_fecha(x, f_busqueda))].sort_values(by='is_vip', ascending=False)
            
            for _, r in df_f2.iterrows():
                try:
                    txt_full2 = f"{r[1]} {r[2]} {r[3]} {r[5]}".upper()
                    if (o_busqueda=="CUALQUIERA" or o_busqueda in safe_str(r[1]).upper()) and \
                       (d_busqueda=="CUALQUIERA" or d_busqueda in safe_str(r[2]).upper()) and \
                       (q_busqueda in txt_full2):
                        
                        nuevo_b2 = '<div class="badge-nuevo">NUEVO</div>' if check_nuevo(r[0]) else ''
                        w_msg2 = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n📦 *CONSULTA POR CARGA*\n🏢 EMPRESA: {r[5]}\n📍 RUTA: {r[1]} -> {r[2]}\n\n¿Sigue disponible?")
                        
                        st.markdown(f'''<div class="{"card-vip" if r["is_vip"] else "card-white"}">{nuevo_b2}
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["is_vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={w_msg2}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a></div>''', unsafe_allow_html=True)
                except: continue

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div style="text-align: center; color: white; padding: 40px; opacity: 0.8; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
    <p style="font-size: 18px; font-weight: bold;">Creado por Ignacio Diaz</p>
    <p>© 2026 RETORNO MATCH VIP - Prohibida la copia total o parcial.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ PANEL DE CONTROL"):
    if st.text_input("PIN DE ACCESO:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Editar Radar:", st.session_state.anuncios)
        st.markdown(f'<a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}" target="_blank">➕ GESTIONAR CLIENTES VIP</a>', unsafe_allow_html=True)
