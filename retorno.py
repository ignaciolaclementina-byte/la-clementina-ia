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

# --- COORDENADAS PARA GEOLOCALIZACIÓN ---
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

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        if not df_ca.empty:
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = []
            for col in df_ca.columns:
                extracted = df_ca[col].astype(str).str.extract(r'REF:(.*)')[0].dropna().tolist()
                refs_borradas.extend(extracted)
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    s = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not s: return "5491111111111"
    if s.startswith("0"): s = s[1:]
    if s.startswith("15"): s = s.replace("15", "", 1)
    return "549" + s if not s.startswith("549") else s

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    val = str(dato).strip().upper().replace(".0", "")
    return val in LISTA_VIPS_GLOBAL

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        if pd.isna(ts): return 999
        return max(0, (datetime.now() - ts).total_seconds() / 60)
    except: return 999

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

# --- 5. ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; }
    .card-hot { background: white !important; border-left: 10px solid #e74c3c !important; border-radius: 15px; padding: 15px; margin-bottom: 10px; color: #333;}
    .card-medium { background: white !important; border-left: 10px solid #2ecc71 !important; border-radius: 15px; padding: 15px; margin-bottom: 10px; color: #333;}
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 15px; margin-bottom: 10px; color: #333;}
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; border-radius: 15px; padding: 15px; margin-bottom: 10px; color: #1b5e20; }
    .route-txt { font-size: 18px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .price-tag { background: #2e7d32; color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 8px; }
    .stats-card { background: rgba(255,255,255,0.1); border-radius: 10px; padding: 10px; text-align: center; color: white; border: 1px solid #f1c40f; }
</style>
""", unsafe_allow_html=True)

# --- 6. CUERPO PRINCIPAL ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Estadísticas
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="stats-card"><b>Cargas Hoy</b><br><span style="font-size:20px; color:#f1c40f;">{len(df_ca_raw)}</span></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stats-card"><b>VIPs</b><br><span style="font-size:20px; color:#f1c40f;">{len(LISTA_VIPS_GLOBAL)}</span></div>', unsafe_allow_html=True)
with c3: st.markdown('<div class="stats-card"><b>Estado</b><br><span style="font-size:20px; color:#f1c40f;">ONLINE</span></div>', unsafe_allow_html=True)
with c4: st.markdown('<div class="stats-card"><b>Ubicación</b><br><span style="font-size:20px; color:#f1c40f;">San Jorge</span></div>', unsafe_allow_html=True)

# Login e Interfaz
user_cuit = st.text_input("🔑 CUIT de Acceso:", "").strip()
soy_vip_actual = es_vip(user_cuit)

PROVINCIAS = ["CUALQUIERA", "SANTA FE", "CORDOBA", "BUENOS AIRES", "ENTRE RIOS"]
colf1, colf2, colf3 = st.columns(3)
with colf1: b_o = st.selectbox("🔍 Origen:", PROVINCIAS)
with colf2: b_d = st.selectbox("🏁 Destino:", PROVINCIAS)
with colf3: b_fecha = st.date_input("📅 Fecha:", hoy)

st.markdown(f'<div style="background:#e74c3c; color:white; padding:5px; text-align:center; border-radius:5px; margin-bottom:20px;"><marquee>Bienvenido al Sistema de Retornos VIP -- Creado por Ignacio Diaz</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA/ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r.iloc[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r.iloc[2]).upper()):
                st.markdown(f'<div class="card-medium"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>🚛 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}<br><a href="https://wa.me/{limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]
        for _, r in df_f2.iterrows():
            minutos = obtener_minutos_desde_publicacion(r.iloc[0])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.warning(f"🔒 EXCLUSIVO VIP - Disponible en {int(TIEMPO_EXCLUSIVO_MIN-minutos)} min")
            else:
                st.markdown(f'<div class="card-vip"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>📦 {r.iloc[3]} | 🏢 {r.iloc[5]}<br><a href="https://wa.me/{limpiar_wsp(r.iloc[4])}" class="btn-wsp">SOLICITAR CARGA</a></div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA (CON TARIFA) ---
with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 SECCIÓN ARRIME COSECHA</h3>", unsafe_allow_html=True)
    ca1, ca2 = st.columns([1, 2])
    with ca1:
        with st.form("f_arrime"):
            z = st.text_input("📍 Zona (Ej: Crispi)")
            d = st.text_input("🌾 Grano/Detalle (Ej: Soja)")
            t = st.text_input("💰 Tarifa (Ej: $13.500)")
            w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                # Se envía el detalle incluyendo la tarifa para que no se pierda
                detalle_completo = f"{d} | TARIFA: {t}"
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME", 
                    "entry.170847116": z, 
                    "entry.576675281": detalle_completo, 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w
                })
                st.success("Publicado!"); time.sleep(1); st.rerun()
    
    with ca2:
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME|COSECHA', case=False)).any(axis=1)]
        for idx, r in df_arr.iterrows():
            # Limpieza de datos segura para evitar KeyError
            l_zona = r.iloc[1] if len(r) > 1 else "S/D"
            l_det = r.iloc[2] if len(r) > 2 else "-"
            l_wsp = r.iloc[4] if len(r) > 4 else ""
            
            st.markdown(f"""
            <div class="card-cosecha">
                <div class="route-txt">📍 {l_zona}</div>
                <div style="margin-top:5px;"><b>DETALLE:</b> {l_det}</div>
                <div style="margin-top:5px;">📱 {ocultar_telefono(l_wsp)}</div>
                <a href="https://wa.me/{limpiar_wsp(l_wsp)}" class="btn-wsp" style="background:#2e7d32">CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"<div style='text-align:center; color:gray; margin-top:50px;'>Creado por <b>Ignacio Diaz</b><br>© 2026 San Jorge, Santa Fe</div>", unsafe_allow_html=True)
