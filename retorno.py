import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. ESTILO DE INTERFAZ
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .camion-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
        overflow: hidden;
    }
    .card-header { background: #f8f9fa; padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
    .btn-wa { background: #25D366; color: white !important; text-align: center; padding: 12px; display: block; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. NAVEGACIÓN
col1, col2, col3 = st.columns(3)
with col3:
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScWcPChu8-wqWSijj9IoA5ES6CunJOJTirhPvqXKHkl_sy9MA/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

# 4. CARGA DE DATOS (UNIFICANDO PESTAÑAS)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_VIEJA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_NUEVA = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    # Leer datos viejos
    df_viejo = pd.read_csv(URL_VIEJA)
    df_viejo = df_viejo[['origen', 'item', 'pago', 'tel']] # Ajustamos al orden viejo
    df_viejo.columns = ['origen', 'destino', 'equipo', 'tel']
    df_viejo['fecha'] = "Histórico"

    # Leer datos nuevos (del formulario)
    df_nuevo = pd.read_csv(URL_NUEVA)
    df_nuevo.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']

    # Juntar todo
    df_total = pd.concat([df_nuevo, df_viejo], ignore_index=True)
    
    # Buscador
    search = st.text_input("", placeholder="🔍 Filtrar por ciudad de destino...")
    if search:
        df_total = df_total[df_total['destino'].str.contains(search
