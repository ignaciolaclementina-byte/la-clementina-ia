import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime

# --- 1. IDENTIDAD Y CONFIGURACIÓN (IGNACIO DIAZ) ---
# Estructura blindada: Creado por Ignacio Diaz
CREADOR = "Ignacio Diaz"
VERSION = "3.1.0 - ULTRA STABLE"

# Google Sheets IDs
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

st.set_page_config(page_title=f"RETORNO MATCH VIP - {CREADOR}", page_icon="⚡", layout="wide")

# --- 2. ESTILOS CSS PREMIUM (SIN DEPENDENCIAS EXTERNAS) ---
st.markdown(f"""
<style>
    /* Fondo y contenedores */
    .stApp {{
        background: #0e1117;
    }}
    
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
    }}
    
    .glass-card:hover {{
        border-color: #f1c40f;
        background: rgba(255, 255, 255, 0.05);
    }}

    /* Títulos y Branding */
    .title-main {{
        font-family: 'Trebuchet MS', sans-serif;
        color: #f1c40f;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 0px;
    }}
    
    /* Barra de Radar */
    .radar-bar {{
        background: linear-gradient(90deg, #f1c40f, #e67e22);
        color: black;
        padding: 5px;
        font-weight: bold;
        text-align: center;
        border-radius: 5px;
        margin-bottom: 20px;
    }}

    /* Footer Blindado */
    .ignacio-footer {{
        text-align: center;
        padding: 40px;
        border-top: 2px solid #f1c40f;
        margin-top: 60px;
        background: #000;
        color: white;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DATOS (RELIABLE) ---
@st.cache_data(ttl=15)
def fetch_data():
    t = int(time.time())
    try:
        # Carga de datos base
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        # VIPs
        vip_data = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper() for x in vip_data[0].dropna().tolist()]
        return ch, ca, vips
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch, df_ca, vips = fetch_data()

# --- 4. HEADER Y DASHBOARD ---
st.markdown(f"<h1 class='title-main'>⚡ RETORNO MATCH ⚡</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:gray;'>DESARROLLADO POR {CREADOR.upper()}</p>", unsafe_allow_html=True)

st.markdown(f"<div class='radar-bar'>SISTEMA ACTIVO • {datetime.now().strftime('%H:%M')} • ZONA SAN JORGE</div>", unsafe_allow_html=True)

# Dashboard de Indicadores (Usando columnas de Streamlit)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("CAMIONES", len(df_ch), delta="Online")
with c2:
    st.metric("CARGAS", len(df_ca), delta="Disponibles", delta_color="normal")
with c3:
    st.metric("ZONA", "SAN JORGE", delta="Principal")
with c4:
    st.metric("AUTOR", "I. DIAZ", delta="Verified")

# --- 5. CUERPO OPERATIVO ---
tab1, tab2, tab3 = st.tabs(["🚛 RADAR DE CAMIONES", "📦 PANEL DE CARGAS", "⚙️ GESTIÓN"])

with tab1:
    st.subheader("Búsqueda Avanzada de Unidades")
    if not df_ch.empty:
        # Filtros rápidos
        search = st.text_input("Filtrar por Chofer, Patente o Destino...", "").upper()
        
        filtered_df = df_ch[df_ch.apply(lambda row: search in row.astype(str).str.upper().values, axis=1)] if search else df_ch
        
        for _, row in filtered_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h3 style="margin:0; color:#f1c40f;">{row.get('CHOFER', 'N/A')}</h3>
                    <p style="margin:0; opacity:0.8;">📍 <b>Origen:</b> {row.get('ORIGEN', '-')}  ➡️  🏁 <b>Destino:</b> {row.get('DESTINO', '-')}</p>
                    <p style="margin:0; font-size: 0.9em;">🚛 {row.get('EQUIPO', '-')} | 🆔 {row.get('PATENTE', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
                # Botón de WhatsApp integrado
                tel = str(row.get('TELEFONO', '')).replace('.0','')
                if tel != '-':
                    msg = urllib.parse.quote(f"Hola {row.get('CHOFER')}, te contacto por la unidad {row.get('PATENTE')} vista en Retorno Match.")
                    st.markdown(f"""<a href="https://wa.me/{tel}?text={msg}" style="text-decoration:none;">
                        <div style="background:#25D366; color:white; text-align:center; padding:8px; border-radius:5px; font-weight:bold; margin-top:-10px; margin-bottom:20px;">
                            CONTACTAR POR WHATSAPP
                        </div></a>""", unsafe_allow_html=True)
    else:
        st.warning("No hay datos de camiones disponibles en este momento.")

with tab2:
    st.subheader("Mercado de Cargas en Tiempo Real")
    if not df_ca.empty:
        st.dataframe(df_ca, use_container_width=True)
    else:
        st.info("Esperando actualización de cargas...")

with tab3:
    st.subheader("Configuración del Sistema")
    st.write(f"Versión del núcleo: {VERSION}")
    st.write(f"Titular de licencia: {CREADOR}")
    if st.button("Forzar Recarga de Datos"):
        st.cache_data.clear()
        st.rerun()

# --- 6. FOOTER DE SEGURIDAD (BRANDEO OBLIGATORIO) ---
st.markdown(f"""
<div class="ignacio-footer">
    <h2 style="margin:0; letter-spacing:10px;">{CREADOR.upper()}</h2>
    <p style="color:#f1c40f; font-size:12px; margin-bottom:20px;">SOLUCIONES TECNOLÓGICAS PARA EL AGRO</p>
    <p style="font-size:14px; opacity:0.7;">
        Este software es propiedad intelectual de <b>{CREADOR}</b>.<br>
        Queda prohibida su copia o distribución sin autorización expresa.
    </p>
    <p style="margin-top:20px; font-weight:bold;">© 2026 SAN JORGE, SANTA FE, ARGENTINA</p>
</div>
""", unsafe_allow_html=True)
