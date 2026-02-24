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
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-white, .card-vip, .card-cosecha, .card-bloqueada { transition: all 0.3s ease-in-out; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .card-white:hover, .card-vip:hover, .card-cosecha:hover { transform: translateY(-5px); box-shadow: 0px 10px 20px rgba(0,0,0,0.4) !important; }
    .card-white { background: white !important; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.3); }
    .card-bloqueada { background: rgba(0,0,0,0.4) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; padding: 30px !important; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-vip-comprar { background-color: #f1c40f; color: black !important; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; font-size: 13px; }
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
    user_cuit = st.text_input("🔑 Ingrese su CUIT (sin puntos ni guiones) para desbloquear:", "").strip()
soy_vip_actual = es_vip(user_cuit)

if user_cuit and soy_vip_actual:
    st.success(f"🌟 MODO VIP ACTIVO: {user_cuit}")
elif user_cuit:
    st.warning("El CUIT ingresado no es VIP. Las cargas nuevas están bloqueadas.")

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar mi Camión</h4>", unsafe_allow_html=True)
        # Aquí va tu formulario de carga de camión...
    
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f2.iterrows():
                minutos = obtener_minutos_desde_publicacion(r[0])
                es_exclusiva = minutos < TIEMPO_EXCLUSIVO_MIN
                
                if es_exclusiva and not soy_vip_actual:
                    msg_vendedor = f"Hola Ignacio, quiero activar mi CUIT {user_cuit} como VIP para ver las cargas exclusivas."
                    link_comprar = f"https://api.whatsapp.com/send?phone={WSP_CONTACTO_ADMIN}&text={urllib.parse.quote(msg_vendedor)}"
                    st.markdown(f'''
                    <div class="card-bloqueada">
                        <span style="font-size: 24px;">🔒</span><br>
                        <b>CARGA EXCLUSIVA PARA MIEMBROS VIP</b><br>
                        <small>Disponible para usuarios estándar en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} minutos</small><br>
                        <a href="{link_comprar}" target="_blank" class="btn-vip-comprar">⭐ SER VIP AHORA</a>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    texto_wsp_ca = f"─── *RETORNO MATCH VIP* ───\n📦 *INTERÉS EN CARGA*\n\n📍 *TRAYECTO:* {r[1]} a {r[2]}\n📦 *CARGA:* {r[3]}\n🏢 *EMPRESA:* {r[5]}"
                    link_wsp_ca = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(texto_wsp_ca)}"
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}
                        <div style="font-size: 18px; font-weight: 900; color: #1e3799;">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}
                        <a href="{link_wsp_ca}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a>
                    </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f'''
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP</p>
    <p>Prohibida la copia total o parcial de esta interfaz.</p>
</div>
''', unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Texto Radar:", st.session_state.anuncios)
        if st.button("LIMPIAR CACHÉ"):
            st.cache_data.clear()
            st.rerun()
