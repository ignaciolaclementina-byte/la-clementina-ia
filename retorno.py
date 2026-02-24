import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30 # Minutos de ventaja para VIPs
WSP_CONTACTO_ADMIN = "5493401525621" # Tu WhatsApp para ventas VIP

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
    try: 
        return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: 
        return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except:
        return 999

# --- 4. ESTILOS VIP PERSONALIZADOS (MEJORADOS POR IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    
    @keyframes pulse { 0% {box-shadow: 0 0 0 0 rgba(241, 196, 15, 0.7);} 70% {box-shadow: 0 0 0 10px rgba(241, 196, 15, 0);} 100% {box-shadow: 0 0 0 0 rgba(241, 196, 15, 0);} }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; animation: pulse 2s infinite; }
    
    .card-white, .card-vip, .card-cosecha, .card-bloqueada { transition: all 0.3s ease-in-out; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .card-white:hover, .card-vip:hover { transform: translateY(-5px); box-shadow: 0px 10px 20px rgba(0,0,0,0.4) !important; }
    .card-white { background: white !important; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; }
    .card-bloqueada { background: rgba(0,0,0,0.6) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 8px; border-radius: 10px; text-decoration: none; font-size: 12px; display: block; text-align: center; margin-top: 5px; opacity: 0.8; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Sistema de identificación
col_id1, col_id2 = st.columns([2,1])
with col_id1:
    user_cuit = st.text_input("🔑 Ingrese su CUIT para acceso completo:", "").strip()
soy_vip_actual = es_vip(user_cuit)

if user_cuit and soy_vip_actual:
    st.success(f"🌟 ACCESO VIP ACTIVADO")
elif user_cuit:
    st.warning("CUIT no registrado como VIP. Cargas nuevas bloqueadas.")

# Banner Radar con animación de pulso
radar_txt = f"⚡ {len(df_ca_raw)} CARGAS HOY -- 🚛 {len(df_ch_raw)} CAMIONES ACTIVOS -- Desarrollado por Ignacio Diaz"
st.markdown(f'<div class="radar-container"><marquee scrollamount="7">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 2: CARGAS (Lógica Early Access Blindada) ---
with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar mi Camión</h4>", unsafe_allow_html=True)
        # Aquí mantienes tus inputs de formulario para Google Forms...
    
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            # Solo mostrar lo de HOY para mayor relevancia
            df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                es_exclusiva = minutos < TIEMPO_EXCLUSIVO_MIN
                
                if es_exclusiva and not soy_vip_actual:
                    msg_ventas = f"Hola Ignacio, quiero activar mi CUIT {user_cuit} para ver las cargas VIP."
                    link_ventas = f"https://api.whatsapp.com/send?phone={WSP_CONTACTO_ADMIN}&text={urllib.parse.quote(msg_ventas)}"
                    st.markdown(f'''
                    <div class="card-bloqueada">
                        🔒 CONTENIDO EXCLUSIVO VIP<br>
                        <small>Visible para todos en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min</small><br>
                        <a href="{link_ventas}" target="_blank" style="color:#f1c40f; text-decoration:none; font-weight:bold;">⭐ QUIERO SER VIP</a>
                    </div>''', unsafe_allow_html=True)
                else:
                    msg_wsp = f"─── *RETORNO MATCH VIP* ───\n📦 *INTERÉS EN CARGA*\n📍 *RUT:* {r[1]} -> {r[2]}\n📦 *CARGA:* {r[3]}\n🏢 *EMPRESA:* {r[5]}"
                    link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(msg_wsp)}"
                    link_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote('¡Mirá esta carga en Retorno Match! ' + msg_wsp)}"
                    
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}
                        <div style="font-size: 18px; font-weight: 900; color: #1e3799;">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}
                        <a href="{link_wsp}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a>
                        <a href="{link_share}" target="_blank" class="btn-share">🔗 COMPARTIR CON UN COLEGA</a>
                    </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f'''
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP</p>
    <p>Prohibida la copia total o parcial de esta interfaz o su lógica de funcionamiento.</p>
</div>
''', unsafe_allow_html=True)

# Panel de administración mantenido
with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        if st.button("LIMPIAR CACHÉ DEL SISTEMA"):
            st.cache_data.clear()
            st.rerun()
