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

# --- 2. SISTEMA ANTI-PAUSA Y AUTO-REFRESH ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 60: # Refresco más corto para datos en vivo
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=15)
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

# --- 4. FUNCIONES AUXILIARES (BLINDAJE IGNACIO DIAZ) ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

def get_equipo_icon(equipo):
    icons = {"Chasis": "🚚", "Semi": "🚛", "Sider": "📦", "Batea": "🏗️", "Térmico": "❄️", "Acoplado": "🚜"}
    return icons.get(equipo, "🚛")

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

# --- 5. INTERFAZ Y ESTILOS (GLASSMORPHISM) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070') !important; background-size: cover !important; }
    
    /* GLASSMORPHISM CARDS */
    .card-glass { 
        background: rgba(255, 255, 255, 0.05) !important; 
        backdrop-filter: blur(10px); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        border-radius: 15px; padding: 20px; margin-bottom: 15px; transition: 0.3s;
    }
    .card-hot { border-left: 8px solid #ff4b2b !important; background: rgba(255, 75, 43, 0.05) !important; }
    .card-vip { border: 2px solid #f1c40f !important; box-shadow: 0 0 15px rgba(241, 196, 15, 0.2); }
    
    .stats-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; text-align: center; border: 1px solid rgba(241,196,15,0.2); }
    .stats-val { font-size: 28px; font-weight: 900; color: #f1c40f; }
    
    .radar-container { background: linear-gradient(90deg, #e74c3c, #c0392b); color: white; padding: 12px; border-radius: 50px; margin: 20px 0; font-weight: bold; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    
    .btn-wsp { background: #25D366; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background: rgba(52, 152, 219, 0.2); color: #3498db !important; border: 1px solid #3498db; padding: 8px; border-radius: 8px; text-decoration: none; font-size: 12px; display: block; text-align: center; margin-top: 5px; }
    
    .legal-footer { text-align: center; color: rgba(255,255,255,0.5); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<h1 style='text-align:center; color:white; font-weight:900;'>⭐ RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="stats-card"><span class="stats-val">{cant_camiones + cant_cargas}</span><br><small>MOVIMIENTOS HOY</small></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="stats-card"><span class="stats-val">{cant_cargas}</span><br><small>CARGAS ACTIVAS</small></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span><br><small>SOCIOS VIP</small></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="stats-card"><span class="stats-val">LIVE</span><br><small>ESTADO RADAR</small></div>', unsafe_allow_html=True)

# --- LOGIN Y FILTROS ---
with st.container():
    col_log, col_space = st.columns([1, 2])
    user_cuit = col_log.text_input("🔑 ACCESO VIP (Ingrese CUIT):", "").strip()
    soy_vip_actual = es_vip(user_cuit)
    if soy_vip_actual: st.success("✅ MODO VIP ACTIVADO")

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

with st.expander("🔍 FILTROS DE BÚSQUEDA AVANZADA"):
    f1, f2, f3, f4 = st.columns(4)
    b_fecha = f1.date_input("Fecha", hoy)
    b_o = f2.selectbox("Origen", PROVINCIAS)
    b_d = f3.selectbox("Destino", PROVINCIAS)
    b_e = f4.selectbox("Equipo", EQUIPOS)
    busqueda_libre = st.text_input("🔎 Buscar por empresa, localidad o producto...").upper()

st.markdown(f'<div class="radar-container"><marquee scrollamount="7">🌾 COSECHA 2026: {cant_camiones} Camiones disponibles para arrime -- Creado por Ignacio Diaz para Retorno Match.</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    f_col, r_col = st.columns([1, 2.5])
    with f_col:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_ca_new", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("🚀 SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()
    with r_col:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: (es_vip(r[4]) or es_vip(r[5])) if len(r) > 5 else False, axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for i, r in df_f.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])) and (busqueda_libre in str(r).upper()):
                    val_a, val_b = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                    cuit, wsp = (val_a, val_b) if len(val_a) == 11 else (val_b, val_a)
                    dist = calcular_distancia(r[1], r[2])
                    card_c = "card-glass" + (" card-vip" if r['vip'] else "") + (" card-hot" if minutos < 60 else "")
                    icon = get_equipo_icon(r[3])
                    
                    st.markdown(f"""
                    <div class="{card_c}">
                        <span style="float:right; color:#f1c40f;">{dist}</span>
                        {f'<div style="background:#f1c40f; color:black; padding:2px 10px; border-radius:10px; font-size:10px; width:fit-content; margin-bottom:5px;">⭐ CHOFER VIP</div>' if r['vip'] else ''}
                        <div style="font-size:1.2rem; font-weight:bold; color:white;">{r[1]} ➔ {r[2]}</div>
                        <div style="color:#bdc3c7; margin:5px 0;">{icon} <b>EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit}</div>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text=Hola, te consulto por el camion {r[1]} a {r[2]}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    f_col2, r_col2 = st.columns([1, 2.5])
    with f_col2:
        st.markdown("### 📢 Publicar Camión")
        with st.form("f_ch_new", clear_on_submit=True):
            op = st.selectbox("Prov. Origen", PROVINCIAS[1:]); ol = st.text_input("Loc. Origen")
            dp = st.selectbox("Prov. Destino", PROVINCIAS[1:]); dl = st.text_input("Loc. Destino")
            et = st.selectbox("Equipo", EQUIPOS[1:]); cid = st.text_input("CUIT"); wn = st.text_input("WhatsApp")
            if st.form_submit_button("🚛 SUBIR CAMIÓN"):
                if validar_cuit(cid):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{op} ({ol})", "entry.1519265625": f"{dp} ({dl})", "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wn})
                    st.cache_data.clear(); st.rerun()
                else: st.error("CUIT INVÁLIDO")
    with r_col2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip) if len(df_ca_raw.columns) > 5 else False
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            
            for i, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                    st.markdown(f'<div class="card-glass" style="text-align:center; border: 1px dashed #f1c40f;">🔒 CARGA EXCLUSIVA VIP<br><small>Disponible para todos en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min</small></div>', unsafe_allow_html=True)
                elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                    txt_share = urllib.parse.quote(f"📢 *NUEVA CARGA*\n📍 Origen: {r[1]}\n🏁 Destino: {r[2]}\n📦 Carga: {r[3]}\n✅ Retorno Match VIP")
                    card_c = "card-glass" + (" card-vip" if r['vip'] else "") + (" card-hot" if minutos < 60 else "")
                    
                    st.markdown(f"""
                    <div class="{card_c}">
                        <div style="font-size:1.2rem; font-weight:bold; color:white;">{r[1]} ➔ {r[2]}</div>
                        <div style="color:#bdc3c7; margin:5px 0;">📦 <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}</div>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">📲 CONTACTAR AHORA</a>
                        <a href="https://api.whatsapp.com/send?text={txt_share}" target="_blank" class="btn-share">📢 DIFUNDIR EN GRUPOS</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 ARRIME DE COSECHA EN VIVO</h3>", unsafe_allow_html=True)
    df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
    cols = st.columns(2)
    for i, (_, r) in enumerate(df_arrime.iterrows()):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="card-glass" style="border-left: 8px solid #2ecc71;">
                <div style="color:#2ecc71; font-weight:bold; font-size:1.1rem;">📍 {r[2]}</div>
                <div style="color:white; margin:10px 0;">{r[3]}</div>
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp" style="background:#2e7d32;">🚜 CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 1.2rem; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP - San Jorge, Santa Fe</p>
    <small>Prohibida la reproducción total o parcial de esta interfaz.</small>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ PANEL CONTROL"):
    if st.text_input("PIN ADMIN:", type="password") == ADMIN_PIN:
        if st.button("BORRAR CACHÉ"):
            st.cache_data.clear(); st.rerun()
