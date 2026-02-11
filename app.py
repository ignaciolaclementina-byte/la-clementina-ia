import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DATOS TÉCNICOS
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO AGRO-REALISTA (Soja de Santa Fe)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Capa de legibilidad para el sol */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.45) !important;
    }

    .titulo { color: #004d00; text-align: center; font-size: 40px; font-weight: bold; text-shadow: 2px 2px 5px white; margin-top: -40px; }
    .sub { color: #1b5e20; text-align: center; font-size: 22px; font-weight: bold; margin-bottom: 30px; text-shadow: 1px 1px 3px white; }
    
    /* Etiquetas en NEGRO TOTAL */
    label, p, span, .stMarkdown { color: #000000 !important; font-weight: 900 !important; font-size: 18px !important; }

    .stButton>button { 
        width: 100%; border-radius: 15px; background-color: #1B5E20 !important; 
        color: white !important; height: 60px; font-size: 20px; border: 2px solid white; font-weight: bold;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 18px; 
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 19px;
    }
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 15px; 
        color: black !important; border-left: 12px solid #1B5E20; box-shadow: 0px 6px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí la imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ESCANEAR Y RECETAR'):
        with st.spinner('Analizando estado del cultivo...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_
