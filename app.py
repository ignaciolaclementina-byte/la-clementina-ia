import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (SISTEMA DE RESPALDO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", # Clave 1
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"  # Clave 2
]

# VADEMÉCUM COMPLETO
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO Y TRADUCCIÓN (CSS)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    
    /* Traducción botones */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    section[data-testid="stFileUploadDropzone"]:before { content: "Arrastrá tu foto acá o"; color: white; font-weight: bold; margin-bottom: 10px; }

    div[data-testid="stCameraInput"] button { font-size: 0px !important; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: white !important;
        padding: 25px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        height: 50px;
    }

    .btn-whatsapp {
