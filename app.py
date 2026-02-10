import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- CSS DEFINITIVO PARA EL CAMPO DE SOJA ---
st.markdown("""
    <style>
    /* 1. Fondo de soja forzado en todas las capas */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

    /* 2. Limpieza de capas que generan el fondo negro */
    [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }

    /* 3. Caja de Informe: Texto Negro sobre Blanco Puro */
    .caja-blanca {
        background-color: #ffffff !important;
        padding: 25px;
        border-radius: 15px;
        color: #000000 !important;
        font-size: 19px;
        line-height: 1.6;
        border-left: 15px solid #2E7D32;
        margin-top: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.8);
    }
    
    .caja-blanca h3, .caja-blanca b, .caja-blanca p, .caja-blanca div {
        color: #000000 !important;
    }

    /* 4. Títulos y Botones */
    .titulo-principal {
        color: #ffffff;
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        text-shadow: 2px 2px 5px #000000;
        margin-top: -50px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid #ffffff !important;
        font-size: 18px;
    }

    /* Etiquetas de los botones de radio y textos sueltos */
    label, p, .stMarkdown {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 3px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUCTURA DE LA APP ---
st.markdown("<div class='titulo-principal'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# Selector de origen de imagen
st.markdown("<br>", unsafe_allow_html=True)
opcion = st.radio("ORIGEN DE LA IMAGEN:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("SUBIR FOTO DEL LOTE", type=["jpg",
