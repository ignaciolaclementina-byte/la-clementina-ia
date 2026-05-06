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
        
        # --- BLINDAJE DE BORRADO (Ignacio Diaz) ---
        if not df_ca.empty:
            mask_borrado = (df_ca.iloc[:, 0].astype(str).str.upper() == 'BORRADO') | \
                           (df_ca.iloc[:, 1].astype(str).str.upper() == 'BORRADO')
            
            refs_para_quitar = []
            filas_instruccion = df_ca[mask_borrado]
            for _, f in filas_instruccion.iterrows():
                match = re.search(r'REF:(.*)', str(f.iloc[2]))
                if match:
                    refs_para_quitar.append(match.group(1).strip())
            
            df_ca = df_ca[~mask_borrado]
            if refs_para_quitar:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_para_quitar)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

ahora = datetime.now()
hoy = ahora.date()

# --- FUNCIONES DE SOPORTE ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        return (ahora - ts).total_seconds() / 60
    except: return 999

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not clean: return "5491111111111"
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 4. INTERFAZ Y ESTILOS (IGNACIO DIAZ) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 10px; padding: 15px; text-align: center; color: white; }
    .stats-val { font-size: 24px; font-weight: 900; color: #f1c40f; display: block; }
    .stats-label { font-size: 12px; text-transform: uppercase; opacity: 0.8; }
    .card-medium { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    .card-old { background: #f8f9fa !important; border-left: 10px solid #95a5a6 !important; color: #777; padding: 15px; margin-bottom: 10px; border-radius: 5px; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 25px; border-radius: 15px; }
    .route-txt { font-size: 19px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 8px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Estadísticas Rápidas
with st.container():
    cs1, cs2, cs3, cs4 = st.columns(4)
    with cs1: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(df_ch_raw)+len(df_ca_raw)}</span><span class="stats-label">Movimientos</span></div>', unsafe_allow_html=True)
    with cs2: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span><span class="stats-label">Miembros VIP</span></div>', unsafe_allow_html=True)
    with cs3: st.markdown(f'<div class="stats-card"><span class="stats-val">ACTIVO</span><span class="stats-label">Sincronización</span></div>', unsafe_allow_html=True)
    with cs4: st.markdown(f'<div class="stats-card"><span class="stats-val">2026</span><span class="stats-label">Versión</span></div>', unsafe_allow_html=True)

# Login CUIT
user_cuit = st.text_input("🔑 CUIT para acceso VIP:", "").strip()
soy_vip_actual = es_vip(user_cuit)

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

c1, c2, c3 = st.columns(3)
with c1: b_fecha = st.date_input("📅 Fecha:", hoy)
with c2: b_o = st.selectbox("🔍 Origen:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 Destino:", PROVINCIAS)

st.markdown(f'<div class="radar-container"><marquee scrollamount="7">SISTEMA RETORNO MATCH VIP -- Creado por Ignacio Diaz.</marquee></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with t1:
    col_f, col_r = st.columns([1, 2.2])
    with col_f:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo, ed, ec, en, ew = st.selectbox("Origen", PROVINCIAS[1:]), st.selectbox("Destino", PROVINCIAS[1:]), st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()
    with col_r:
        if not df_ch_raw.empty:
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r.iloc[2]).upper()):
                    link = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}"
                    st.markdown(f'<div class="card-old"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>🚛 {r.iloc[3]}</b> | 📱 {ocultar_telefono(r.iloc[5])}<br><a href="{link}" target="_blank" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            op, dp, et, cid, wn = st.selectbox("Origen", PROVINCIAS[1:]), st.selectbox("Destino", PROVINCIAS[1:]), st.selectbox("Equipo", EQUIPOS[1:]), st.text_input("CUIT"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": op, "entry.1519265625": dp, "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wn})
                st.cache_data.clear(); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.iloc[:, 1].str.contains("ARRIME", na=False)]
            df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r.iloc[0])
                if (b_o=="CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r.iloc[2]).upper()):
                    if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                        st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)}m restantes)</div>', unsafe_allow_html=True)
                    else:
                        link = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}"
                        st.markdown(f'<div class="card-medium"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>📦 {r.iloc[3]}</b> | 🏢 {r.iloc[5]}<br><a href="{link}" target="_blank" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA (ARRIME) ---
with t3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 ARRIME DE COSECHA</h3>", unsafe_allow_html=True)
    ca1, ca2 = st.columns([1, 2.2])
    with ca1:
        with st.form("f_arr", clear_on_submit=True):
            zl, gd, wa = st.text_input("📍 Zona"), st.text_input("🌾 Grano/Detalle"), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": zl, "entry.576675281": gd, "entry.1930562861": "COSECHA", "entry.466540450": wa})
                st.cache_data.clear(); st.rerun()
    with ca2:
        if not df_ca_raw.empty:
            df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].str.contains("ARRIME", na=False)]
            for i, (idx, r) in enumerate(df_arr.iterrows()):
                # FIX: USAMOS .iloc PARA EVITAR EL KEYERROR DE LA IMAGEN
                st.markdown(f'<div class="card-cosecha"><div class="route-txt" style="color:#2e7d32;">📍 {r.iloc[2]}</div>{r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">CONTACTAR</a></div>', unsafe_allow_html=True)
                if st.session_state.get('admin_mode', False):
                    if st.button(f"🗑️ BORRAR #{i}", key=f"del_{idx}"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.170847116": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}", "entry.1930562861": "SISTEMA", "entry.466540450": "0"})
                        st.cache_data.clear(); st.rerun()

# --- PIE DE PÁGINA ---
st.markdown(f'<div class="legal-footer">Creado por Ignacio Diaz<br><b>© 2026 RETORNO MATCH VIP</b></div>', unsafe_allow_html=True)

with st.expander("⚙️"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        if st.button("LIMPIAR CACHÉ"): st.cache_data.clear(); st.rerun()
