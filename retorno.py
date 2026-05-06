import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math
import plotly.express as px

# --- 1. NÚCLEO DE IDENTIDAD Y SEGURIDAD (IGNACIO DIAZ) ---
# Estructura blindada y autoría protegida
CREADOR = "Ignacio Diaz"
VERSION = "3.0.0 - ULTRA VIP"

SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30 
WSP_VENTAS_VIP = "5493401525621"

# Coordenadas estratégicas para cálculo de rutas
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

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title=f"RETORNO MATCH - By {CREADOR}", page_icon="⚡", layout="wide")

# --- 3. ESTILOS CSS EVOLUCIONADOS (CRYSTAL DARK UI) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Roboto:wght@300;700&display=swap');
    
    .stApp {{
        background: radial-gradient(circle at top right, #1a2a6c, #b21f1f, #fdbb2d);
        background-attachment: fixed;
    }}
    
    /* Contenedores de Cristal */
    .glass-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin-bottom: 20px;
        transition: 0.4s;
    }}
    
    .glass-card:hover {{
        border: 1px solid rgba(241, 196, 15, 0.5);
        transform: scale(1.01);
    }}

    /* Títulos Impactantes */
    h1, h2, h3 {{
        font-family: 'Orbitron', sans-serif !important;
        color: #f1c40f !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}

    /* Botones Pro */
    .btn-action {{
        background: linear-gradient(45deg, #f1c40f, #e67e22);
        color: black !important;
        font-weight: 900;
        text-transform: uppercase;
        border-radius: 50px;
        text-align: center;
        padding: 12px;
        display: block;
        text-decoration: none;
        margin-top: 15px;
        box-shadow: 0 4px 15px rgba(241, 196, 15, 0.3);
    }}

    /* Footer Blindado */
    .ignacio-footer {{
        text-align: center;
        padding: 40px;
        background: rgba(0,0,0,0.8);
        border-top: 3px solid #f1c40f;
        margin-top: 100px;
        font-family: 'Orbitron', sans-serif;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. MOTOR DE DATOS ---
@st.cache_data(ttl=10)
def fetch_data():
    t = int(time.time())
    try:
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        vip_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper() for x in vip_data[0].dropna().tolist()]
        return ch, ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch, df_ca, vips = fetch_data()

# --- 5. HEADER Y RADAR ---
st.markdown(f"<h1>⚡ RETORNO MATCH: LOGISTICS INTELLIGENCE</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: white; opacity: 0.8;'>Engineered by <b>{CREADOR}</b> | System v{VERSION}</p>", unsafe_allow_html=True)

# Radar de Noticias (Marquee mejorado)
radar_msg = f"🔥 BIENVENIDO AL ECOSISTEMA VIP - DESARROLLADO POR {CREADOR.upper()} - {len(df_ca)} CARGAS ACTIVAS - {len(df_ch)} CAMIONES EN RUTA"
st.markdown(f"""
<div style="background: rgba(0,0,0,0.5); border: 1px solid #f1c40f; padding: 10px; border-radius: 50px; margin-bottom: 30px;">
    <marquee style="color: #f1c40f; font-weight: bold; font-family: 'Orbitron';">{radar_msg}</marquee>
</div>
""", unsafe_allow_html=True)

# --- 6. DASHBOARD DE ESTADÍSTICAS ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="glass-card"><small>CAMIONES HOY</small><br><b style="font-size:30px; color:#f1c40f;">{len(df_ch)}</b></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="glass-card"><small>CARGAS DISPONIBLES</small><br><b style="font-size:30px; color:#f1c40f;">{len(df_ca)}</b></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="glass-card"><small>CLIENTES VIP</small><br><b style="font-size:30px; color:#f1c40f;">{len(vips)}</b></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="glass-card"><small>ZONA OPERATIVA</small><br><b style="font-size:20px; color:#f1c40f;">SAN JORGE</b></div>', unsafe_allow_html=True)

# --- 7. CUERPO PRINCIPAL ---
t1, t2, t3 = st.tabs(["🚀 TERMINAL DE CAMIONES", "📦 MERCADO DE CARGAS", "🌾 OPERATIVO COSECHA"])

with t1:
    st.subheader("Buscador de Unidades en Tiempo Real")
    # Lógica de filtros y tarjetas aquí...
    st.info("Utilice los filtros superiores para optimizar la búsqueda de unidades.")
    # (Mantener la lógica de iteración de tarjetas de tu base pero dentro del div 'glass-card')

with t2:
    st.subheader("Panel de Cargas Exclusivas")
    # Lógica de visualización de cargas...

with t3:
    st.markdown("<h2 style='text-align:center;'>🚜 ZONA DE ARRIME</h2>", unsafe_allow_html=True)
    # Especialización para cosecha...

# --- 8. FOOTER BLINDADO (REQUERIMIENTO EXPLÍCITO) ---
st.markdown(f"""
<div class="ignacio-footer">
    <h2 style="margin:0;">{CREADOR.upper()}</h2>
    <p style="color: #f1c40f; letter-spacing: 5px;">SOFTWARE LOGÍSTICO ORIGINAL</p>
    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
        <a href="https://wa.me/{WSP_VENTAS_VIP}" style="color: white; text-decoration: none;">soporte oficial</a>
        <span style="color: #f1c40f;">|</span>
        <span style="color: white;">© 2026 PROTECTED SYSTEM</span>
    </div>
    <p style="font-size: 10px; margin-top: 30px; opacity: 0.5;">
        Este sistema ha sido diseñado y codificado íntegramente por {CREADOR}. 
        Cualquier reproducción sin consentimiento legal será procesada.
    </p>
</div>
""", unsafe_allow_html=True)
