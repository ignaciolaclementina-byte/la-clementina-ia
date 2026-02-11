import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVES Y VADEMECUM
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. SKIN "CARBONO AGRO" (Elegante y Moderno)
st.markdown("""
    <style>
    /* Fondo Oscuro Elegante */
    .stApp {
        background-color: #0e1117 !important;
    }
    
    /* Contenedor con borde verde neón */
    [data-testid="stAppViewContainer"] {
        border-top: 5px solid #2ecc71;
    }

    /* Títulos Impactantes */
    .titulo { 
        color: #2ecc71; text-align: center; font-size: 38px; font-weight: 800; 
        letter-spacing: 1px; margin-bottom: 0px; 
    }
    .sub { 
        color: #888; text-align: center; font-size: 16px; margin-bottom: 30px; 
        text-transform: uppercase; letter-spacing: 2px;
    }
    
    /* Estilo de los controles */
    label, p, span { color: #ffffff !important; font-weight: 500 !important; }

    /* Botón de Acción Principal */
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #2ecc71 !important;
        color: #0e1117 !important; height: 55px; font-size: 18px; border: none; 
        font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #27ae60 !important; }

    /* Botón WhatsApp */
    .btn-wa {
        display: block; background-color: transparent; color: #25D366 !important; 
        padding: 15px; border-radius: 8px; text-decoration: none; text-align: center; 
        font-weight: bold; border: 2px solid #25D366; font-size: 18px;
    }
    
    /* Caja de Informe (Estilo Papel Técnico) */
    .reporte-box {
        background-color: #1c2128 !important; padding: 25px; border-radius: 12px;
        color: #e6edf3 !important; border-left: 5px solid #2ecc71;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5); margin-top: 20px;
        line-height: 1.6;
    }
    .reporte-box b { color: #2ecc71 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>Tecnología para el Agro • San Jorge</div>", unsafe_allow_html=True)

with st.container():
    opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 USAR CÁMARA", "📁 SUBIR ARCHIVO"], horizontal=True)
