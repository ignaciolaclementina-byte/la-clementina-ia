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

# --- 2. GESTIÓN DE SESIÓN ---
if "admin_mode" not in st.session_state: st.session_state.admin_mode = False
if "anuncios" not in st.session_state: st.session_state.anuncios = "¡Bienvenido!"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except: return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 5. INTERFAZ OPTIMIZADA PARA MÓVILES ---
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

st.markdown("""
<style>
    /* Reset para móviles */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Contenedor de Tarjetas */
    .card-mobile {
        background: #1c2128;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        border: 1px solid #30363d;
    }
    
    /* Textos adaptativos */
    .route-title { 
        font-size: 1.1rem; 
        font-weight: bold; 
        color: #539bf5; 
        line-height: 1.2;
    }
    
    /* Botón gigante para pulgar en móvil */
    .btn-wsp-mobile {
        background: #238636;
        color: white !important;
        text-align: center;
        padding: 14px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        font-weight: bold;
        margin-top: 10px;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    /* Ocultar elementos innecesarios en pantallas chicas si fuera necesario */
    @media (max-width: 640px) {
        .stTabs [data-baseweb="tab"] { font-size: 12px; padding: 10px 5px; }
    }
</style>
""", unsafe_allow_html=True)

# SIDEBAR (Simplificado)
with st.sidebar:
    st.title("🛡️ Admin")
    pin = st.text_input("PIN", type="password")
    st.session_state.admin_mode = (pin == ADMIN_PIN)
    user_cuit = st.text_input("🔑 CUIT VIP")

# CABECERA
st.markdown(f'<div style="background:#21262d; padding:10px; border-radius:8px; margin-bottom:15px; border:1px solid #30363d; text-align:center;"><marquee scrollamount="5" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee></div>', unsafe_allow_html=True)

# Filtros (En móvil se apilan solos)
busqueda = st.text_input("🔎 BUSCAR (Ej: ROSARIO, MAIZ)").upper()

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    if st.session_state.admin_mode:
        with st.expander("➕ REGISTRAR CAMIÓN"):
            with st.form("f1"):
                o_p = st.text_input("Origen")
                d_p = st.text_input("Destino")
                eq = st.text_input("Equipo")
                cu = st.text_input("CUIT")
                ws = st.text_input("WhatsApp")
                if st.form_submit_button("PUBLICAR"):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                    st.rerun()

    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if busqueda in str(r).upper():
                st.markdown(f"""<div class="card-mobile">
                    <div class="route-title">📍 {r.iloc[1]} <br>➔ {r.iloc[2]}</div>
                    <div style="margin-top:8px; font-size:0.9rem; opacity:0.8;">
                        🚛 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}
                    </div>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp-mobile">OFERTAR MI CARGA</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    if st.session_state.admin_mode:
        with st.expander("➕ NUEVA CARGA"):
            with st.form("f2"):
                o = st.text_input("Carga")
                d = st.text_input("Descarga")
                m = st.text_input("Mercadería")
                en = st.text_input("Empresa")
                w = st.text_input("WhatsApp")
                if st.form_submit_button("PUBLICAR"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m, "entry.1930562861": en, "entry.466540450": w})
                    st.rerun()

    if not df_ca_raw.empty:
        df_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for _, r in df_v.iterrows():
            if busqueda in str(r).upper():
                st.markdown(f"""<div class="card-mobile" style="border-left: 5px solid #238636;">
                    <div class="route-title" style="color:#2ecc71;">📦 {r.iloc[1]} <br>➔ {r.iloc[2]}</div>
                    <div style="margin-top:8px; font-size:0.9rem;">
                        <b>{r.iloc[3]}</b> | {r.iloc[5]}
                    </div>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp-mobile" style="background:#2980b9;">PEDIR VIAJE</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 3: COSECHA ---
with tab3:
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains('ARRIME', case=False)]
        for _, r in df_arr.iterrows():
            if busqueda in str(r).upper():
                st.markdown(f"""<div class="card-mobile" style="border-left: 5px solid #4caf50;">
                    <div class="route-title">🌾 ZONA: {r.iloc[2]}</div>
                    <div style="margin-top:5px;">{r.iloc[3]}</div>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp-mobile" style="background:#4caf50;">CONTACTAR</a>
                </div>""", unsafe_allow_html=True)

# FOOTER
st.markdown("<div style='text-align:center; padding:20px; opacity:0.4; font-size:0.8rem;'>Ignacio Diaz - 2026</div>", unsafe_allow_html=True)
