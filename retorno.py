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

# --- 2. SISTEMA ANTI-PAUSA Y CONTADOR ---
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
        
        # --- BLINDAJE DE BORRADO (Ignacio Diaz) ---
        if not df_ca.empty:
            # Filtro por palabra 'BORRADO'
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            # Filtro por Referencia de Timestamp (REF:...)
            refs_borradas = []
            for col in df_ca.columns:
                extracted = df_ca[col].astype(str).str.extract(r'REF:(.*)')[0].dropna().tolist()
                refs_borradas.extend(extracted)
            
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                # El timestamp suele estar en la primera columna (índice 0)
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- 4. FUNCIONES AUXILIARES (BLINDADAS) ---
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

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        if pd.isna(ts): return 999
        diff = datetime.now() - ts
        return max(0, diff.total_seconds() / 60)
    except: return 999

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

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
            return f"📍 {int(r * c)} km aprox."
        return ""
    except: return ""

def validar_cuit(cuit):
    cuit = "".join(filter(str.isdigit, str(cuit)))
    if len(cuit) != 11: return False
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    try:
        aux = sum(int(cuit[i]) * base[i] for i in range(10))
        aux = 11 - (aux % 11)
        if aux == 11: aux = 0
        if aux == 10: aux = 9
        return aux == int(cuit[10])
    except: return False

# --- 5. UI/UX Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .card-white, .card-vip, .card-cosecha, .card-hot, .card-medium, .card-old { border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-hot { background: white !important; border-left: 10px solid #e74c3c !important; }
    .card-medium { background: white !important; border-left: 10px solid #2ecc71 !important; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; opacity: 0.9; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.3); }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; border-radius: 15px; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 12px; margin-bottom: 10px; display: inline-block; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; font-size: 13px; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; text-align: center; font-weight: bold; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 24px; font-weight: 900; color: #f1c40f; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 6. CUERPO PRINCIPAL ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Panel Estadísticas
cstats1, cstats2, cstats3, cstats4 = st.columns(4)
cant_mov = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0
with cstats1: st.markdown(f'<div class="stats-card"><span class="stats-val">{cant_mov}</span>Cargas Hoy</div>', unsafe_allow_html=True)
with cstats2: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span>Miembros VIP</div>', unsafe_allow_html=True)
with cstats3: st.markdown(f'<div class="stats-card"><span class="stats-val">LIVE</span>Sistema Activo</div>', unsafe_allow_html=True)
with cstats4: st.markdown(f'<div class="stats-card"><span class="stats-val">S.J.</span>Santa Fe</div>', unsafe_allow_html=True)

# Filtros y Login
with st.container():
    c_log1, c_log2 = st.columns([2, 1])
    with c_log1:
        user_cuit = st.text_input("🔑 CUIT de Acceso:", "").strip()
        soy_vip_actual = es_vip(user_cuit) if user_cuit else False
        if soy_vip_actual: st.success("✅ ACCESO VIP ACTIVO")

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

with st.container():
    cf1, cf2, cf3, cf4 = st.columns(4)
    with cf1: b_fecha = st.date_input("📅 Fecha:", hoy)
    with cf2: b_o = st.selectbox("🔍 Origen:", PROVINCIAS)
    with cf3: b_d = st.selectbox("🏁 Destino:", PROVINCIAS)
    with cf4: b_e = st.selectbox("🚛 Equipo:", EQUIPOS)

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">Bienvenido al Sistema de Retornos VIP -- Creado por Ignacio Diaz</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA/ARRIME"])

# --- LÓGICA TABS (EXTRACTO BLINDADO) ---
with tab1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_r1:
        if not df_ch_raw.empty:
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f.iterrows():
                try:
                    minutos = obtener_minutos_desde_publicacion(r[0])
                    v_chofer = es_vip(r[4]) or es_vip(r[5])
                    link = f"https://wa.me/{limpiar_wsp(r[5])}"
                    card_c = "card-vip" if v_chofer else ("card-hot" if minutos < 60 else "card-medium")
                    if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                        st.markdown(f'<div class="{card_c}">{"<div class=\'vip-label\'>⭐ CHOFER VIP</div>" if v_chofer else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div>🚛 {r[3]} | 📱 {ocultar_telefono(r[5])}<br><a href="{link}" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)
                except: continue

with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f2.iterrows():
                try:
                    minutos = obtener_minutos_desde_publicacion(r[0])
                    v_empresa = es_vip(r[5])
                    if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                        st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)}m restantes)</div>', unsafe_allow_html=True)
                    elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                        card_c = "card-vip" if v_empresa else ("card-hot" if minutos < 60 else "card-medium")
                        st.markdown(f'<div class="{card_c}">{"<div class=\'vip-label\'>⭐ EMPRESA VIP</div>" if v_empresa else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div>📦 {r[3]} | 🏢 {r[5]}<br><a href="https://wa.me/{limpiar_wsp(r[4])}" class="btn-wsp">SOLICITAR CARGA</a></div>', unsafe_allow_html=True)
                except: continue

with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 SECCIÓN ARRIME COSECHA</h3>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        with st.form("f_arrime"):
            z = st.text_input("📍 Zona"); d = st.text_input("🌾 Detalle"); w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME", "entry.170847116": z, "entry.576675281": d, "entry.1930562861": "COSECHA", "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with col_a2:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME|COSECHA', case=False)).any(axis=1)]
        for idx, r in df_arr.iterrows():
            # Acceso por posición blindado para evitar KeyError
            l_zona = r.iloc[1] if len(r) > 1 else "S/D"
            l_det = r.iloc[2] if len(r) > 2 else "-"
            l_wsp = r.iloc[4] if len(r) > 4 else "0"
            st.markdown(f'<div class="card-cosecha"><div class="route-txt">📍 {l_zona}</div>{l_det}<br><a href="https://wa.me/{limpiar_wsp(l_wsp)}" class="btn-wsp" style="background:#2e7d32">CONTACTAR</a></div>', unsafe_allow_html=True)
            if st.session_state.get('admin_mode', False):
                if st.button(f"🗑️ BORRAR", key=f"del_{idx}"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                    st.cache_data.clear(); st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f"""<div style='text-align:center; color:white; padding:50px;'>
    <p style='font-size:18px;'>Creado por <b>Ignacio Diaz</b></p>
    <p style='color:#f1c40f;'>© 2026 RETORNO MATCH VIP - San Jorge, Santa Fe</p>
</div>""", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO ADMIN ACTIVO")
