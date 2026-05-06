import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN ESTRUCTURAL (IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ADMIN_PIN = "1323" 

st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")

# --- 2. CSS DE ALTA GAMA (BLINDAJE VISUAL) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    .main-header { text-align: center; padding: 20px; border-bottom: 2px solid #f1c40f; margin-bottom: 30px; }
    .data-card {
        background: #111; 
        border: 1px solid #333; 
        border-radius: 10px; 
        padding: 20px; 
        margin-bottom: 15px;
        border-left: 8px solid #f1c40f;
    }
    .route-header { color: #f1c40f; font-size: 22px; font-weight: 900; margin-bottom: 10px; }
    .btn-wsp {
        background: #25D366; color: white !important; text-align: center;
        padding: 12px; border-radius: 8px; display: block;
        text-decoration: none; font-weight: bold; margin-top: 15px;
    }
    .stats-box {
        background: #1a1a1a; padding: 15px; border-radius: 10px;
        text-align: center; border: 1px solid #f1c40f;
    }
    .footer { text-align: center; padding: 50px; border-top: 1px solid #333; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DATOS ULTRA-RÁPIDO ---
@st.cache_data(ttl=2)
def fetch_master():
    t = int(time.time())
    try:
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        return ch, ca
    except:
        return pd.DataFrame(), pd.DataFrame()

df_ch, df_ca = fetch_master()

# --- 4. CABECERA PROFESIONAL ---
st.markdown(f"""
<div class="main-header">
    <h1 style="margin:0; letter-spacing: 2px;">RETORNO MATCH <span style="color:#f1c40f;">VIP</span></h1>
    <p style="color:gray;">Diseño de Infraestructura: <b>Ignacio Diaz</b></p>
</div>
""", unsafe_allow_html=True)

# Indicadores Reales
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="stats-box"><h3>{len(df_ch)}</h3><p>CHOFERES EN RUTA</p></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="stats-box"><h3>{len(df_ca)}</h3><p>CARGAS DISPONIBLES</p></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="stats-box"><h3>LIVE</h3><p>ESTADO DEL NÚCLEO</p></div>', unsafe_allow_html=True)

# --- 5. FILTROS ESTRATÉGICOS ---
st.write("")
busqueda = st.text_input("🔍 BUSCADOR GLOBAL (Ciudad, Empresa, Camión):").upper()

# --- 6. VISUALIZACIÓN DE DATOS (ELIMINANDO EL ERROR DE "NO SE VE") ---
t1, t2 = st.tabs(["📦 MERCADO DE CARGAS", "🚛 RADAR DE CHOFERES"])

with t1:
    if not df_ca.empty:
        # Filtrado
        df_ca_filt = df_ca[df_ca.apply(lambda x: busqueda in str(x).upper(), axis=1)] if busqueda else df_ca
        
        for _, r in df_ca_filt.iterrows():
            # Limpieza de código (sin comas ni decimales)
            codigo_limpio = str(r[0]).split('.')[0].replace(',','')
            
            st.markdown(f"""
            <div class="data-card">
                <div class="route-header">{r[1]} ➔ {r[2]}</div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><b>PRODUCTO:</b> {r[3]}</div>
                    <div><b>EMPRESA:</b> {r[5]}</div>
                    <div><b>REF:</b> #{codigo_limpio}</div>
                </div>
                <a href="https://wa.me/{str(r[4]).replace('.0','')}" class="btn-wsp">SOLICITAR CARGA POR WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Error de conexión con la base de datos de Cargas.")

with t2:
    if not df_ch.empty:
        df_ch_filt = df_ch[df_ch.apply(lambda x: busqueda in str(x).upper(), axis=1)] if busqueda else df_ch
        for _, r in df_ch_filt.iterrows():
            st.markdown(f"""
            <div class="data-card" style="border-left-color: #3498db;">
                <div class="route-header" style="color: #3498db;">{r[1]} ➔ {r[2]}</div>
                <p>🚛 <b>CHOFER:</b> {r[4]} | <b>EQUIPO:</b> {r[3]}</p>
                <a href="https://wa.me/{str(r[5]).replace('.0','')}" class="btn-wsp" style="background:#075E54;">CONTACTAR CHOFER</a>
            </div>
            """, unsafe_allow_html=True)

# --- 7. FOOTER DE PROPIEDAD INTELECTUAL ---
st.markdown(f"""
<div class="footer">
    <h2 style="color:#f1c40f;">CREADO POR IGNACIO DIAZ Y SUS LEGALES</h2>
    <p><b>ESTRUCTURA NACHO 360° - VERSIÓN INDUSTRIAL 2026</b></p>
    <p style="color:gray; font-size:12px;">Queda prohibida la copia o reproducción de esta interfaz sin el consentimiento legal de Ignacio Diaz.</p>
</div>
""", unsafe_allow_html=True)
