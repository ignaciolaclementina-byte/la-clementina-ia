import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- FORZAR DISEÑO DE CAMPO ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

st.markdown("""
    <style>
    /* Este bloque elimina el fondo negro de Streamlit */
    .stAppViewContainer {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=1280&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Limpiamos capas superiores que puedan estar tapando */
    .stMainBlockContainer, .stAppHeader {
        background-color: transparent !important;
    }

    /* Estilo del título */
    .titulo {
        color: #C5E1A5;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        margin-top: -50px;
    }

    /* Botones y Radio */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 55px;
        background-color: #33691E;
        color: white;
        font-weight: bold;
        border: 2px solid #ffffff;
    }

    /* Caja de resultado (Bien legible) */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 20px;
        border-radius: 15px;
        color: #1b5e20;
        font-size: 16px;
        margin-top: 20px;
        border-left: 10px solid #33691E;
    }

    /* Forzar color de texto en labels */
    label, p, .stMarkdown {
        color: white !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA FOTO:", ["Cámara", "Galería"], horizontal=True)

if opcion == "Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("SUBIR IMAGEN", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 ANALIZAR CULTIVO'):
        with st.spinner('Analizando síntomas...'):
            try:
                # Detección de modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((500, 500))
                
                prompt = "Actuá como agrónomo. Analizá la imagen y da: Diagnóstico, Causa y Tratamiento."
                response = model.generate_content([prompt, img])
                
                st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
