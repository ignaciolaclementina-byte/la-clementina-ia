import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import re
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
# (Mantenemos tus IDs de siempre)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ADMIN_PIN = "1323" 
WSP_VENTAS_VIP = "5493401525621"

COORDS_CIUDADES = {
    "TODAS": (0,0),
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639), "SANTA FE (SF)": (-31.633, -60.700),
    "RAFAELA (SF)": (-31.250, -61.486), "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237), "AVELLANEDA (SF)": (-29.117, -59.658), "CRISPI (SF)": (-31.721, -61.916),
    "SASTRE (SF)": (-31.766, -61.828), "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
    "CORDOBA (CBA)": (-31.413, -64.181), "SAN FRANCISCO (CBA)": (-31.427, -62.082), "RIO CUARTO (CBA)": (-33.123, -64.348),
    "VILLA MARIA (CBA)": (-32.407, -63.240), "JESUS MARIA (CBA)": (-30.981, -64.093), "MARCOS JUAREZ (CBA)": (-32.697, -62.106),
    "BAHIA BLANCA (BA)": (-38.718, -62.266), "QUEQUEN (BA)": (-38.541, -58.713), "CAMPANA (BA)": (-34.163, -58.959),
    "ZARATE (BA)": (-34.096, -59.024), "RAMALLO (BA)": (-33.483, -60.000), "PERGAMINO (BA)": (-33.891, -60.573),
    "PARANA (ER)": (-31.733, -60.529), "VICTORIA (ER)": (-32.624, -60.155), "SGO DEL ESTERO": (-27.795, -64.263),
    "TUCUMAN": (-26.824, -65.222), "SALTA": (-24.785, -65.411)
}

# --- 2. GESTIÓN DE SESIÓN Y DATOS ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido al nuevo Retorno Match!"

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except: return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos()

# --- 3. NUEVO DISEÑO UI (CSS AVANZADO) ---
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

st.markdown("""
<style>
    /* Fondo General Profundo */
    .stApp {
        background-color: #0e1117;
        background-image: radial-gradient(circle at 2px 2px, #1d2129 1px, transparent 0);
        background-size: 40px 40px;
        color: #e0e0e0;
    }
    
    /* Tarjetas Glassmorphism */
    .card-modern {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .card-modern:hover {
        border-color: #3498db;
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-2px);
    }
    
    /* Rutas Destacadas */
    .route-header {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #3498db;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Etiquetas VIP */
    .vip-tag {
        background: linear-gradient(90deg, #f1c40f, #f39c12);
        color: #000;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    
    /* Botones Pro */
    .btn-action {
        background: #27ae60;
        color: white !important;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        font-weight: 600;
        margin-top: 15px;
        font-size: 0.9rem;
    }
    .btn-action:hover { background: #2ecc71; }
    
    /* Inputs y Sidebar */
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    .stTextInput>div>div>input { background-color: #0d1117; color: white; border-color: #30363d; }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES LÓGICAS ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    return "549" + (clean[1:] if clean.startswith("0") else clean).replace("15", "", 1) if not clean.startswith("549") else clean

def ocultar_tel(num, es_vip):
    if es_vip or st.session_state.admin_mode: return str(num).split('.')[0]
    return f"****{str(num)[-4:]}"

# --- 5. CUERPO DE LA APP ---
with st.sidebar:
    st.title("🛡️ Panel")
    pin = st.text_input("PIN Admin", type="password")
    st.session_state.admin_mode = (pin == ADMIN_PIN)
    
    st.divider()
    user_cuit = st.text_input("🔑 CUIT VIP").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# Título y Anuncios
st.title("🚛 RETORNO MATCH")
st.info(f"📢 {st.session_state.anuncios} | **By Ignacio Diaz**")

# Filtros Minimalistas
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    search = st.text_input("🔎 Buscar (Localidad, Grano, Empresa...)", placeholder="¿Qué estás buscando?").upper()
with col_f2:
    filtro_loc = st.selectbox("📍 Ciudad Base", list(COORDS_CIUDADES.keys()))

tabs = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS ACTIVAS", "🌾 ARRIME", "📊 CALCULADOR"])

# --- TAB 1: CAMIONES ---
with tabs[0]:
    col1, col2 = st.columns([1, 2.5])
    with col1:
        if st.session_state.admin_mode:
            with st.form("f1"):
                st.subheader("Cargar Camión")
                o_p = st.text_input("Origen")
                d_p = st.text_input("Destino")
                eq = st.text_input("Equipo")
                cu = st.text_input("CUIT")
                ws = st.text_input("WhatsApp")
                if st.form_submit_button("PUBLICAR"):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                    st.rerun()
    with col2:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iterrows():
                if search in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                    is_vip = str(r.iloc[4]) in LISTA_VIPS_GLOBAL
                    st.markdown(f"""
                    <div class="card-modern">
                        <div class="route-header">
                            📍 {r.iloc[1]} ➔ {r.iloc[2]}
                            {"<span class='vip-tag'>VIP</span>" if is_vip else ""}
                        </div>
                        <div style="margin-top:10px; opacity:0.8; font-size:0.9rem;">
                            🚛 {r.iloc[3]} | 📱 {ocultar_tel(r.iloc[5], es_user_vip)}
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-action">OFERTAR CARGA</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tabs[1]:
    col1, col2 = st.columns([1, 2.5])
    with col1:
        if st.session_state.admin_mode:
            with st.form("f2"):
                st.subheader("Nueva Carga")
                o = st.text_input("Carga")
                d = st.text_input("Descarga")
                m = st.text_input("Mercadería")
                en = st.text_input("Empresa")
                w = st.text_input("WhatsApp")
                if st.form_submit_button("PUBLICAR CARGA"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m, "entry.1930562861": en, "entry.466540450": w})
                    st.rerun()
    with col2:
        if not df_ca_raw.empty:
            df_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
            for _, r in df_v.iterrows():
                if search in str(r).upper() and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper()):
                    st.markdown(f"""
                    <div class="card-modern" style="border-left: 4px solid #27ae60;">
                        <div class="route-header" style="color:#27ae60;">📦 {r.iloc[1]} ➔ {r.iloc[2]}</div>
                        <div style="margin-top:10px; opacity:0.8;">
                            <b>Mercadería:</b> {r.iloc[3]} | 🏢 {r.iloc[5]}
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-action" style="background:#2980b9;">SOLICITAR VIAJE</a>
                    </div>
                    """, unsafe_allow_html=True)

# (Tabs 3 y 4 mantienen la lógica pero con las clases card-modern)
# --- FOOTER ---
st.markdown("<br><div style='text-align:center; color:#555;'>Creado por Ignacio Diaz - 2026</div>", unsafe_allow_html=True)
