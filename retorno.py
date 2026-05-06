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

# --- 2. MOTOR DE LIMPIEZA DE DATOS (REQUERIMIENTO: SIN COMAS NI DECIMALES) ---
def limpiar_identificador(dato):
    """Limpia CUITs, IDs y códigos: elimina .0 y comas de miles"""
    s = str(dato).replace(".0", "").replace(",", "").strip()
    return "".join(filter(str.isdigit, s))

def format_wsp(num):
    """Formatea el número para el enlace directo de WhatsApp"""
    clean = limpiar_identificador(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

# --- 3. CARGA DE DATOS OPTIMIZADA ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Ignacio Diaz
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            df_ca = df_ca[~mask]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [limpiar_identificador(x) for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. INTERFAZ PROFESIONAL ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide", page_icon="🚛")

# Diseño CSS Moderno y Veloz
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e6edf3; }
    .card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    .vip-card { border-left: 5px solid #f1c40f !important; }
    .route { font-size: 1.2rem; font-weight: bold; color: #f1c40f; text-transform: uppercase; }
    .btn-wsp {
        background: #238636; color: white !important; text-align: center;
        padding: 10px; border-radius: 6px; display: block;
        text-decoration: none; font-weight: bold; margin-top: 10px;
    }
    .footer { text-align: center; padding: 40px; border-top: 1px solid #30363d; color: #8b949e; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()

# Encabezado
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"<p style='color:#f1c40f;'>Diseño de Sistema: <b>Ignacio Diaz</b></p>", unsafe_allow_html=True)

# Filtros Globales
col1, col2, col3 = st.columns(3)
with col1: s_o = st.text_input("📍 ORIGEN:").upper()
with col2: s_d = st.text_input("🏁 DESTINO:").upper()
with col3: s_q = st.text_input("🔍 PRODUCTO/EMPRESA:").upper()

t1, t2 = st.tabs(["🚀 CAMIONES DISPONIBLES", "📦 CARGAS DISPONIBLES"])

with t1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if (s_o in str(r[1]).upper()) and (s_d in str(r[2]).upper()) and (s_q in str(r).upper()):
                cuit = limpiar_identificador(r[4])
                es_vip = cuit in LISTA_VIPS
                st.markdown(f"""
                <div class="card {'vip-card' if es_vip else ''}">
                    <div class="route">{r[1]} ➔ {r[2]} {"⭐ VIP" if es_vip else ""}</div>
                    <p>🚛 <b>EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit}</p>
                    <a href="https://wa.me/{format_wsp(r[5])}" class="btn-wsp">ENVIAR PROPUESTA</a>
                </div>
                """, unsafe_allow_html=True)

with t2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if (s_o in str(r[1]).upper()) and (s_d in str(r[2]).upper()) and (s_q in str(r).upper()):
                st.markdown(f"""
                <div class="card" style="border-left: 5px solid #3498db;">
                    <div class="route" style="color:#3498db;">{r[1]} ➔ {r[2]}</div>
                    <p>📦 <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}</p>
                    <a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp" style="background:#3498db;">POSTULARSE</a>
                </div>
                """, unsafe_allow_html=True)

# Pie de Página Legal
st.markdown(f"""
<div class="footer">
    <h3>CREADO POR IGNACIO DIAZ</h3>
    <p>ESTRUCTURA NACHO 360° | SISTEMA DE LOGÍSTICA PROFESIONAL</p>
    <p style="font-size:0.7rem;">© 2026 RETORNO MATCH. Prohibida su reproducción parcial o total.</p>
</div>
""", unsafe_allow_html=True)
