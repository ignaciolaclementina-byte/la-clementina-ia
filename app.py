import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de tu API Key
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- DISEÑO AVANZADO (CSS) ---
st.markdown("""
    <style>
    /* 1. Fondo de imagen con efecto de desenfoque */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* 2. Tarjeta central contenedora */
    .main-card {
        background-color: rgba(38, 39, 48, 0.85);
        padding: 30px;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }

    /* 3. Títulos y Textos */
    .titulo {
        color: #9CCC65;
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .subtitulo {
        color: #ffffff;
        text-align: center;
        font-size: 16px;
        margin-bottom: 30px;
        opacity: 0.8;
    }

    /* 4. Botones de selección */
    .stButton>button {
        border-radius: 12px;
        height: 50px;
        font-weight: bold;
        transition: 0.3s;
    }

    /* 5. Botón de diagnóstico (El grande verde) */
    .diag-btn>div>button {
        background-color: #558B2F !important;
        color: white !important;
        width: 100%;
        border: none !important;
        font-size: 18px !important;
        margin-top: 15px;
    }

    /* 6. Caja de resultado (Informe Técnico) */
    .reporte-container {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #558B2F;
        color: #1b5e20;
        font-size: 16px;
        margin-top: 20px;
    }
    
    /* Ocultar etiquetas de Streamlit para limpieza */
    label { color: white !important; font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ESTRUCTURA DE LA APP ---
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Diagnóstico de Precisión - San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# Tarjeta de entrada
with st.container():
    st.markdown("<div class='main-card'>", unsafe_allow_html=True)
    
    opcion = st.radio("Seleccioná origen:", ["Cámara", "Galería"], horizontal=True)
    
    if opcion == "Cámara":
        archivo = st.camera_input("Capturá la muestra")
    else:
        archivo = st.file_uploader("Subí la imagen del cultivo", type=["jpg", "png", "jpeg"])
    
    st.markdown("</div>", unsafe_allow_html=True)

# Botón de acción y resultado
if archivo:
    st.image(archivo, use_container_width=True, caption="Muestra cargada")
    
    st.markdown("<div class='diag-btn'>", unsafe_allow_html=True)
    if st.button('🚀 GENERAR INFORME TÉCNICO'):
        with st.spinner('Procesando datos agrícolas...'):
            try:
                # Lógica de la IA
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(archivo).convert('RGB')
                img.thumbnail((700, 700))
                
                prompt = "Como ingeniero agrónomo, analizá la imagen y da: 1. Diagnóstico, 2. Causa probable, 3. Tratamiento sugerido."
                response = model.generate_content([prompt, img])
                
                # Despliegue del reporte con estilo
                st.markdown(f"<div class='reporte-container'><b>📋 INFORME DEL ESPECIALISTA:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error técnico: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; color:white; opacity:0.6; font-size:12px;'>V.4.0 - Desarrollado para el sector agropecuario</p>", unsafe_allow_html=True)
