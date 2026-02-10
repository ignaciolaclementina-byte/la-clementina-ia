import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu API Key
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- ESTE BLOQUE MATA EL FONDO NEGRO Y PONE LA SOJA ---
st.markdown("""
    <style>
    /* Forzamos el fondo en todos los contenedores posibles */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://cdn.pixabay.com/photo/2016/09/21/18/00/soy-1685253_1280.jpg");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

    /* Caja para que el contenido no flote en el aire */
    .stMarkdown, .stButton, .stFileUploader {
        text-shadow: 1px 1px 2px black;
    }

    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        color: #1a1a1a;
        border-left: 8px solid #2e7d32;
        text-shadow: none !important;
    }

    h1, h2, h3, p, label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
st.markdown("<h1 style='text-align: center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Diagnóstico de Precisión - San Jorge</p>", unsafe_allow_html=True)

opcion = st.radio("Seleccioná origen:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí tu foto", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            try:
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                img = Image.open(archivo).convert('RGB')
                
                prompt = "Sos un agrónomo. Analizá la imagen y da: Diagnóstico, Causa y Tratamiento."
                response = model.generate_content([prompt, img])
                
                st.markdown(f"<div class='reporte-box'><b>📋 INFORME:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
