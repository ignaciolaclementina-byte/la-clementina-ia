import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

# URLs de Google Forms para envíos automáticos
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

# --- 2. MOTOR DE LIMPIEZA DE DATOS (REQUERIMIENTO: SIN COMAS NI DECIMALES) ---
def limpiar_texto(dato):
    """Elimina .0, comas y espacios basura para que CUITs y IDs sean perfectos"""
    s = str(dato).replace(".0", "").replace(",", "").strip()
    return s

def format_wsp(num):
    """Asegura que el enlace de WhatsApp sea siempre válido"""
    clean = "".join(filter(str.isdigit, limpiar_texto(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

# --- 3. CARGA DE DATOS ULTRA-RÁPIDA ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time()) # Anti-cache de Google
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Profesional
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            df_ca = df_ca[~mask]
            
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [limpiar_texto(x) for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. INTERFAZ PROFESIONAL "HIGH-SPEED" ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide", page_icon="🚛")

# CSS para máxima velocidad y estética corporativa
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .card {
        background: #161b22; border-radius: 10px; padding: 20px;
        border: 1px solid #30363d; margin-bottom: 15px;
    }
    .vip-card { border: 1px solid #f1c40f !important; background: #1c1a0c !important; }
    .route { color: #f1c40f; font-size: 20px; font-weight: bold; text-transform: uppercase; }
    .btn-wsp {
        background: #238636; color: white !important; text-align: center;
        padding: 10px; border-radius: 6px; display: block;
        text-decoration: none; font-weight: bold; margin-top: 10px;
    }
    .footer { text-align: center; padding: 40px; border-top: 1px solid #30363d; color: #8b949e; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()

# Encabezado
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"<p style='color:gray;'>Sistema desarrollado por <b>Ignacio Diaz</b></p>", unsafe_allow_html=True)

# Filtros inteligentes
c1, c2, c3 = st.columns(3)
with c1: search_o = st.text_input("📍 ORIGEN:").upper()
with c2: search_d = st.text_input("🏁 DESTINO:").upper()
with c3: search_txt = st.text_input("🔍 BUSCAR (PRODUCTO/EMPRESA):").upper()

tab1, tab2 = st.tabs(["🚀 CAMIONES DISPONIBLES", "📦 CARGAS DISPONIBLES"])

# --- VISTA DE CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if (search_o in str(r[1]).upper()) and (search_d in str(r[2]).upper()) and (search_txt in str(r).upper()):
                cuit = limpiar_texto(r[4])
                es_vip = cuit in LISTA_VIPS
                
                st.markdown(f"""
                <div class="card {'vip-card' if es_vip else ''}">
                    <div class="route">{r[1]} ➔ {r[2]} {"⭐ VIP" if es_vip else ""}</div>
                    <p>🚛 <b>EQUIPO:</b> {r[3]} | 🆔 <b>ID:</b> {cuit}</p>
                    <a href="https://wa.me/{format_wsp(r[5])}" class="btn-wsp">CONTACTAR AHORA</a>
                </div>
                """, unsafe_allow_html=True)

# --- VISTA DE CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if (search_o in str(r[1]).upper()) and (search_d in str(r[2]).upper()) and (search_txt in str(r).upper()):
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid #3498db;">
                    <div class="route" style="color:#3498db;">{r[1]} ➔ {r[2]}</div>
                    <p>📦 <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}</p>
                    <a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp" style="background:#3498db;">POSTULARSE</a>
                </div>
                """, unsafe_allow_html=True)

# --- CIERRE LEGAL ---
st.markdown(f"""
<div class="footer">
    <h3>CREADO POR IGNACIO DIAZ</h3>
    <p>ESTRUCTURA NACHO 360° - SISTEMA DE LOGÍSTICA PROFESIONAL</p>
    <p style="font-size:10px;">© 2026. Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
