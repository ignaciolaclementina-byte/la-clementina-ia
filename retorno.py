import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN Y BLINDAJE (POR IGNACIO DIAZ) ---
ST_TITLE = "RETORNO MATCH - GESTIÓN 360"
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CARGAS = "1267917528"
GID_CHOFERES = "1392659349"
CREADOR = "Ignacio Diaz"

st.set_page_config(page_title=ST_TITLE, page_icon="🚛", layout="wide")

# --- 2. ESTILOS PERSONALIZADOS ---
st.markdown(f"""
<style>
    .main {{ background-color: #f5f7f9; }}
    .stMetric {{ background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    .card-carga {{
        background: white; border-left: 5px solid #007bff; padding: 15px;
        border-radius: 8px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .footer {{ text-align: center; padding: 20px; color: #666; font-size: 0.9em; border-top: 1px solid #ddd; margin-top: 30px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE DATOS ---
@st.cache_data(ttl=60)
def get_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    return pd.read_csv(url)

def format_whatsapp(tel, msg):
    # Limpieza de formato solicitada: sin comas ni decimales
    tel_clean = str(tel).split('.')[0].replace(',', '').replace(' ', '')
    if not tel_clean.startswith('549'): tel_clean = '549' + tel_clean
    return f"https://wa.me/{tel_clean}?text={urllib.parse.quote(msg)}"

# --- 4. BARRA LATERAL (CONTROL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830305.png", width=100)
    st.title("Panel de Control")
    page = st.radio("Ir a:", ["📊 Dashboard", "📦 Cargas Disponibles", "🚛 Directorio Choferes"])
    st.divider()
    st.info(f"Sistema desarrollado por: \n**{CREADOR}**")

# --- 5. LÓGICA DE PÁGINAS ---
df_cargas = get_data(GID_CARGAS)

if page == "📊 Dashboard":
    st.header("Resumen Logístico")
    c1, c2, c3 = st.columns(3)
    c1.metric("Cargas Activas", len(df_cargas))
    c2.metric("Nuevas hoy", "5") # Ejemplo estático
    c3.metric("Zonas Críticas", "Santa Fe / BS AS")
    
    st.subheader("Tendencia de Cargas")
    st.bar_chart(df_cargas['ORIGEN'].value_counts().head(5))

elif page == "📦 Cargas Disponibles":
    st.header("Buscador de Cargas en Tiempo Real")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1: ori = st.selectbox("Origen:", ["Todos"] + list(df_cargas['ORIGEN'].unique()))
    with col_f2: dest = st.selectbox("Destino:", ["Todos"] + list(df_cargas['DESTINO'].unique()))
    
    filt = df_cargas.copy()
    if ori != "Todos": filt = filt[filt['ORIGEN'] == ori]
    if dest != "Todos": filt = filt[filt['DESTINO'] == dest]
    
    for _, row in filt.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="card-carga">
                <h4>📍 {row['ORIGEN']} ➔ 🏁 {row['DESTINO']}</h4>
                <p><b>Producto:</b> {row['PRODUCTO']} | <b>Tarifa:</b> {row.get('TARIFA', 'A convenir')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            msg_wsp = f"Hola! Me interesa la carga {row['ORIGEN']} a {row['DESTINO']} para mi camión."
            link = format_whatsapp(row['TELEFONO'], msg_wsp)
            st.link_button(f"📲 Contactar por Carga", link)

# --- 6. FOOTER PROFESIONAL ---
st.markdown(f"""
<div class="footer">
    <p><b>Creado por {CREADOR}</b><br>
    Sistema de Gestión de Fletes y Logística de Granos<br>
    © 2026 Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
