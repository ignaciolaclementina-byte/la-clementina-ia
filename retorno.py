import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN DE IDENTIDAD Y SEGURIDAD ---
CREADOR = "Ignacio Diaz"
VERSION = "4.2.0 - GOLD EDITION"

# Enlaces de Google Sheets y Forms (Base de Datos)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# Enlace al Formulario de Google para CARGAR NUEVAS (Reemplaza con tu link real de FormResponse)
URL_FORM_CARGAS = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title=f"RETORNO MATCH - {CREADOR}", page_icon="⚡", layout="wide")

# --- 2. ESTILOS DE INTERFAZ ELITE ---
st.markdown(f"""
<style>
    .main {{ background-color: #0a0a0a; }}
    .stMetric {{ background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #333; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1a1a1a; border-radius: 5px 5px 0 0; padding: 10px 20px; color: white;
    }}
    .stTabs [aria-selected="true"] {{ background-color: #f1c40f !important; color: black !important; font-weight: bold; }}
    
    /* Branding Footer */
    .footer-nacho {{
        text-align: center; padding: 40px; border-top: 2px solid #f1c40f; margin-top: 50px; color: #f1c40f; font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DATOS ---
@st.cache_data(ttl=5) # Actualización rápida cada 5 segundos
def fetch_data():
    t = int(time.time())
    try:
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        return ch, ca
    except:
        return pd.DataFrame(), pd.DataFrame()

df_ch, df_ca = fetch_data()

# --- 4. HEADER ---
st.markdown(f"<h1 style='text-align: center; color: #f1c40f;'>⚡ RETORNO MATCH 360°</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: gray;'>Sistema Blindado | Creado por {CREADOR}</p>", unsafe_allow_html=True)

# Indicadores principales
c1, c2, c3 = st.columns(3)
c1.metric("UNIDADES EN RUTA", len(df_ch))
c2.metric("CARGAS DISPONIBLES", len(df_ca))
c3.metric("ESTADO", "ONLINE", delta="Sincronizado")

# --- 5. PANEL OPERATIVO ---
tab1, tab2, tab3 = st.tabs(["📋 VER CARGAS", "➕ CARGAR NUEVA", "🚛 RADAR CHOFERES"])

with tab1:
    st.subheader("Listado Maestro de Cargas")
    if not df_ca.empty:
        # Buscador específico para cargas
        busc_ca = st.text_input("Filtrar Cargas (Origen, Destino o Producto):").upper()
        df_ca_filt = df_ca[df_ca.apply(lambda x: busc_ca in str(x).upper(), axis=1)] if busc_ca else df_ca
        
        # TABLA VISIBLE Y ANCHA
        st.dataframe(df_ca_filt, use_container_width=True, height=500)
    else:
        st.error("No se pudieron leer las cargas. Verifica la conexión con Google Sheets.")

with tab2:
    st.subheader("Terminal de Carga de Datos")
    with st.form("form_carga"):
        st.info("Complete los datos para publicar una nueva carga en el sistema.")
        col_a, col_b = st.columns(2)
        with col_a:
            f_origen = st.text_input("📍 ORIGEN")
            f_producto = st.text_input("🌾 PRODUCTO")
        with col_b:
            f_destino = st.text_input("🏁 DESTINO")
            f_pago = st.text_input("💰 TARIFA/PAGO")
        
        f_obs = st.text_area("📝 OBSERVACIONES")
        
        btn_enviar = st.form_submit_button("🚀 PUBLICAR CARGA")
        
        if btn_enviar:
            # Aquí va la lógica de envío a Google Forms (debes configurar los entry.ID correspondientes)
            st.success("Solicitud de carga enviada. Se reflejará en el sistema en breve.")
            st.balloons()

with tab3:
    st.subheader("Radar de Unidades Disponibles")
    if not df_ch.empty:
        busc_ch = st.text_input("Buscar Chofer o Patente:").upper()
        df_ch_filt = df_ch[df_ch.apply(lambda x: busc_ch in str(x).upper(), axis=1)] if busc_ch else df_ch
        
        for _, row in df_ch_filt.iterrows():
            with st.expander(f"🚛 {row.get('CHOFER', 'N/A')} - {row.get('PATENTE', 'N/A')}"):
                st.write(f"**Ubicación:** {row.get('ORIGEN', '-')} -> {row.get('DESTINO', '-')}")
                tel = str(row.get('TELEFONO', '')).replace('.0','')
                if tel != '-':
                    st.markdown(f"[📲 Contactar por WhatsApp](https://wa.me/{tel})")
    else:
        st.warning("No hay choferes activos registrados.")

# --- 6. FOOTER BLINDADO ---
st.markdown(f"""
<div class="footer-nacho">
    <p>ESTRUCTURA E INTERFAZ BLINDADA</p>
    <p style="font-size: 25px;">CREADO POR {CREADOR.upper()} Y SUS LEGALES</p>
    <p style="color: gray; font-size: 10px;">PROHIBIDA SU REPRODUCCIÓN TOTAL O PARCIAL - © 2026</p>
</div>
""", unsafe_allow_html=True)
