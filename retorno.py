import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
WSP_VENTAS_VIP = "5493401525621"

# --- 2. FUNCIONES DE LIMPIEZA DE DATOS (REQUERIMIENTO: SIN COMAS NI DECIMALES) ---
def format_id(dato):
    """Limpia CUITs e IDs: quita .0 y comas de miles"""
    s = str(dato).replace(".0", "").replace(",", "").strip()
    return "".join(filter(str.isdigit, s))

def format_wsp(num):
    """Formatea el número para enlace directo de WhatsApp"""
    clean = format_id(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

# --- 3. MOTOR DE DATOS SEGUROS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Ignacio Diaz
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [format_id(x) for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. INTERFAZ PROFESIONAL ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide", page_icon="🚛")

# CSS para Diseño High-End
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .main-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px; padding: 25px;
        border-left: 5px solid #f1c40f;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .route-title { font-size: 24px; font-weight: 800; color: #f1c40f; text-transform: uppercase; margin-bottom: 10px; }
    .data-row { font-size: 16px; margin-bottom: 5px; }
    .btn-wsp {
        background: #25D366; color: white !important;
        text-align: center; padding: 12px;
        border-radius: 10px; display: block;
        text-decoration: none; font-weight: bold;
        transition: 0.3s; margin-top: 15px;
    }
    .btn-wsp:hover { background: #128C7E; transform: scale(1.02); }
    .footer { text-align: center; padding: 50px; border-top: 1px solid #333; margin-top: 100px; color: #888; }
    .vip-tag { background: #f1c40f; color: black; padding: 2px 10px; border-radius: 5px; font-weight: 900; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()

# Título y Autoría
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"<p style='color:#f1c40f;'>Diseño de Sistema: <b>Ignacio Diaz</b></p>", unsafe_allow_html=True)

# Filtros Globales
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1: search_o = st.text_input("ORIGEN:").upper()
    with c2: search_d = st.text_input("DESTINO:").upper()
    with c3: search_gen = st.text_input("BUSCAR PRODUCTO/EMPRESA:").upper()

# --- 5. VISUALIZACIÓN DE DATOS ---
t1, t2 = st.tabs(["🚀 CAMIONES DISPONIBLES", "📦 CARGAS DISPONIBLES"])

with t1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if (search_o in str(r[1]).upper()) and (search_d in str(r[2]).upper()) and (search_gen in str(r).upper()):
                cuit_limpio = format_id(r[4])
                is_vip = cuit_limpio in LISTA_VIPS
                
                st.markdown(f"""
                <div class="main-card">
                    <div class="route-title">
                        {r[1]} ➔ {r[2]} 
                        {"<span class='vip-tag'>⭐ VIP</span>" if is_vip else ""}
                    </div>
                    <div class="data-row"><b>EQUIPO:</b> {r[3]}</div>
                    <div class="data-row"><b>CHOFER / CUIT:</b> {cuit_limpio}</div>
                    <a href="https://wa.me/{format_wsp(r[5])}" class="btn-wsp">ENVIAR PROPUESTA WHATSAPP</a>
                </div>
                """, unsafe_allow_html=True)

with t2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if (search_o in str(r[1]).upper()) and (search_d in str(r[2]).upper()) and (search_gen in str(r).upper()):
                st.markdown(f"""
                <div class="main-card" style="border-left-color: #3498db;">
                    <div class="route-title" style="color:#3498db;">{r[1]} ➔ {r[2]}</div>
                    <div class="data-row"><b>CARGA:</b> {r[3]}</div>
                    <div class="data-row"><b>EMPRESA:</b> {r[5]}</div>
                    <a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp" style="background:#3498db;">POSTULARSE A CARGA</a>
                </div>
                """, unsafe_allow_html=True)

# --- 6. FOOTER LEGAL (IGNACIO DIAZ) ---
st.markdown(f"""
<div class="footer">
    <h2 style="color:#f1c40f;">CREADO POR IGNACIO DIAZ</h2>
    <p>ESTRUCTURA NACHO 360° - BLINDAJE DE DATOS ACTIVO</p>
    <p style="font-size:10px;">© 2026 RETORNO MATCH VIP. Prohibida la copia de este código fuente.</p>
</div>
""", unsafe_allow_html=True)
