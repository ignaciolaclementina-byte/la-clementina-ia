import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DATOS (No tocar)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO BLINDADO (Con respaldo verde)
st.markdown("""
    <style>
    /* 1. Fondo base VERDE (por si falla la foto) */
    .stApp {
        background-color: #2E7D32 !important; 
    }
    
    /* 2. Intentar cargar la foto de soja encima */
    .stApp {
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Soybean_cultivation.jpg/1280px-Soybean_cultivation.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }

    /* Panel blanco para leer bien */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.6);
    }

    /* Títulos y textos */
    .titulo { color: #004d00; text-align: center; font-size: 36px; font-weight: 900; text-shadow: 2px 2px 4px white; margin-top: -30px; }
    .sub { color: #1b5e20; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px; }
    
    label, p, div.stMarkdown { color: #000000 !important; font-weight: 800 !important; font-size: 16px; }

    /* Botones */
    .stButton>button { 
        width: 100%; border-radius: 10px; background-color: #1B5E20 !important; 
        color: white !important; height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px; margin-top: 15px;
    }
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 10px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. PANTALLA PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí tu foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR CULTIVO'):
        with st.spinner('Consultando al Ingeniero IA...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Sos un Agrónomo experto de campo argentino. Analizá la imagen. Diagnóstico y receta usando solo: {VADEMECUM}. Sé breve y técnico."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito =
