import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card-viaje { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black !important; border-left: 10px solid #2ecc71; }
    .card-viaje h3, .card-viaje p { color: black !important; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN (Debe coincidir con [gsheets] en tus Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu Excel (la que pasaste recién)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9lMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Leemos la pestaña 'cargas'
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        
        if df is not None and
