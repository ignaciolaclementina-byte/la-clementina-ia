import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; box-shadow: 0 4px 8px rgba(0,0,0,0.5); }
    .card h3 { margin: 0; color: #2ecc71; }
    .stButton>button { background-color: #2ecc71; color: white; width: 100%; font-weight: bold; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN (Mantenemos la lectura por CSV para que sea rápido)
# NOTA: Para escribir, usaremos un link de Google Form oculto que es 100% confiable.
URL_LECTURA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR DISPONIBLES", "📤 PUBLICAR AHORA"])

with tab1:
    try:
        df = pd.read_csv(URL_LECTURA)
        df.columns = df.columns.str.strip().str.lower()
        
        # Buscador rápido
        search = st.text_input("Filtrar por ciudad...", "").lower()
        
        for _, r in df.dropna(subset=['origen']).iterrows():
