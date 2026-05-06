import streamlit as st
import pandas as pd
import time
import requests
import math
from datetime import datetime

# --- CONFIGURACIÓN DE ESTRUCTURA (IGNACIO DIAZ) ---
#
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
ADMIN_PIN = "1323" 

# Coordenadas aproximadas para cálculo de flete
PROVINCIAS_COORDS = {
    "SANTA FE": (-31.63, -60.70), "CORDOBA": (-31.41, -64.18), 
    "BUENOS AIRES": (-34.60, -58.38), "ENTRE RIOS": (-31.73, -60.52)
}

def calcular_distancia(p1, p2):
    """Calcula distancia usando Haversine para logística"""
    if p1 in PROVINCIAS_COORDS and p2 in PROVINCIAS_COORDS:
        lat1, lon1 = PROVINCIAS_COORDS[p1]
        lat2, lon2 = PROVINCIAS_COORDS[p2]
        r = 6371 # Radio Tierra km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
        return int(2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a)))
    return None

# --- ESTILOS PERSONALIZADOS ---
st.set_page_config(page_title="Retorno Match - Ignacio Diaz", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .card { 
        background: #1d2129; 
        border-left: 5px solid #f1c40f; 
        padding: 15px; 
        border-radius: 10px; 
        margin-bottom: 10px;
    }
    .vip-tag { background: #f1c40f; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; }
    .footer { text-align: center; padding: 20px; color: #888; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE DATOS ---
@st.cache_data(ttl=60)
def cargar_datos():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}"
    df = pd.read_csv(url).fillna("-")
    # Limpieza de códigos (quitar comas/decimales)
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace(".0", "", regex=False).str.replace(",", "", regex=False)
    return df

# --- INTERFAZ PRINCIPAL ---
st.title("🚛 Retorno Match VIP")
st.subheader("Gestión Logística Profesional")

col1, col2 = st.columns([1, 3])

with col1:
    st.info("Filtros de Búsqueda")
    origen = st.selectbox("Origen", ["TODOS"] + list(PROVINCIAS_COORDS.keys()))
    equipo = st.multiselect("Tipo de Equipo", ["Sider", "Chasis", "Batea", "Semi"])
    
    st.markdown("---")
    st.write("🔧 **Panel de Control**")
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

with col2:
    df = cargar_datos()
    
    # Simulación de Radar de Cargas
    for index, row in df.iterrows():
        dist = calcular_distancia(row.get('Origen Prov', ''), row.get('Destino Prov', ''))
        dist_text = f" | 📍 {dist} km aprox." if dist else ""
        
        with st.container():
            st.markdown(f"""
            <div class="card">
                <span class="vip-tag">DISPONIBLE</span>
                <h3 style='margin:10px 0;'>{row.get('Origen', 'N/A')} ➔ {row.get('Destino', 'N/A')}</h3>
                <p>📦 <b>Carga:</b> {row.get('Mercaderia', 'Cereal')} {dist_text}</p>
                <p>📱 <b>Contacto:</b> {row.get('WhatsApp', 'Consultar')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de WhatsApp Profesional
            msg = f"Hola, vi tu carga de {row.get('Origen')} a {row.get('Destino')} en Retorno Match. Me interesa."
            wsp_link = f"https://wa.me/{row.get('WhatsApp')}?text={msg.replace(' ', '%20')}"
            st.link_button("📞 Contactar por WhatsApp", wsp_link)

# --- PIE DE PÁGINA BLINDADO ---
#
st.markdown("---")
st.markdown(f"""
    <div class="footer">
        <p>Creado por <b>Ignacio Diaz</b></p>
        <p>Sistema Blindado - Estructura Nacho v2026.5</p>
    </div>
""", unsafe_allow_html=True)
