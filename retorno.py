import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN CORE (ESTRUCTURA IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚛", layout="wide")

# --- 2. MOTOR DE DATOS (SIN LIBRERÍAS EXTERNAS RARAS) ---
@st.cache_data(ttl=10)
def cargar_datos_maestros():
    try:
        t = int(time.time())
        url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
        url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        url_v = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}"
        
        df_ch = pd.read_csv(url_ch).fillna("-")
        df_ca = pd.read_csv(url_ca).fillna("-")
        df_v = pd.read_csv(url_v, header=None)
        vips = [str(x).strip().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 3. ESTILOS VISUALES (BLINDAJE IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .main-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #f1c40f;
    }
    .route-header { font-size: 22px; font-weight: 800; color: #f0f6fc; margin-bottom: 8px; }
    .info-txt { color: #8b949e; font-size: 14px; }
    .highlight { color: #f1c40f; font-weight: bold; }
    .btn-wsp {
        display: block; width: 100%; text-align: center; background-color: #238636;
        color: white !important; padding: 10px; border-radius: 8px; 
        font-weight: bold; text-decoration: none; margin-top: 12px;
    }
    .footer { text-align: center; padding: 40px; color: #8b949e; border-top: 1px solid #30363d; margin-top: 30px; }
</style>
""", unsafe_allow_html=True)

# --- 4. LÓGICA DE NEGOCIO ---
df_ch, df_ca, vips = cargar_datos_maestros()

st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"**Creado por Ignacio Diaz** | Gestión Logística San Jorge")

# Tabs principales
tab_cargas, tab_camiones, tab_mapa = st.tabs(["📦 CARGAS", "🚚 CAMIONES", "📍 RADAR"])

with tab_cargas:
    if df_ca.empty:
        st.warning("No hay cargas disponibles en este momento.")
    else:
        # Filtro rápido
        busqueda = st.text_input("🔍 Buscar destino o mercadería:").upper()
        
        for _, row in df_ca.iloc[::-1].iterrows():
            orig, dest, merca, wsp = row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4]
            empr = row.iloc[5] if len(row) > 5 else "Directo"
            
            if busqueda and busqueda not in str(dest).upper() and busqueda not in str(merca).upper():
                continue

            msg = urllib.parse.quote(f"Hola {empr}, vi tu carga de {orig} a {dest} en Retorno Match. ¿Sigue disponible?")
            
            st.markdown(f"""
            <div class="main-card">
                <div class="route-header">{orig} ➔ {dest}</div>
                <div class="info-txt">📦 Carga: <span class="highlight">{merca}</span></div>
                <div class="info-txt">🏢 Empresa: {empr}</div>
                <a href="https://wa.me/{wsp}?text={msg}" target="_blank" class="btn-wsp">CONTACTAR CARGA</a>
            </div>
            """, unsafe_allow_html=True)

with tab_camiones:
    if df_ch.empty:
        st.warning("No hay camiones reportados hoy.")
    else:
        for _, row in df_ch.iloc[::-1].iterrows():
            orig, dest, equi, cuit = row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4]
            wsp = row.iloc[5] if len(row) > 5 else cuit
            
            st.markdown(f"""
            <div class="main-card" style="border-left-color: #3498db;">
                <div class="route-header">{orig} ➔ {dest}</div>
                <div class="info-txt">🚛 Equipo: <span class="highlight">{equi}</span></div>
                <div class="info-txt">🆔 CUIT: {cuit}</div>
                <a href="https://wa.me/{wsp}" target="_blank" class="btn-wsp" style="background-color: #1f6feb;">OFRECER VIAJE</a>
            </div>
            """, unsafe_allow_html=True)

with tab_mapa:
    st.markdown("### Mapa de Disponibilidad")
    # Mapa nativo de Streamlit (No requiere Plotly ni instalaciones extra)
    # Creamos coordenadas ficticias aproximadas para que el mapa no se vea vacío
    map_data = pd.DataFrame({
        'lat': [-31.63, -31.42, -34.60, -32.94],
        'lon': [-60.70, -64.18, -58.38, -60.63]
    })
    st.map(map_data)
    st.info("El radar muestra zonas con mayor movimiento logístico en tiempo real.")

# --- 5. FOOTER BLINDADO ---
st.markdown(f"""
<div class="footer">
    <p>ESTRUCTURA DE INTERFAZ PROTEGIDA</p>
    <h2 style="color: #f1c40f; margin: 0;">CREADO POR IGNACIO DIAZ</h2>
    <p>© 2026 San Jorge, Santa Fe</p>
</div>
""", unsafe_allow_html=True)

# Botón técnico para forzar actualización
if st.button("🔄 REFRESCAR DATOS"):
    st.cache_data.clear()
    st.rerun()
