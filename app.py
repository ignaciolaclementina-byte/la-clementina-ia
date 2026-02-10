import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- DISEÑO CON FONDO DE SOJA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

st.markdown("""
    <style>
    /* Fondo de imagen con capa de contraste */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Título principal */
    .titulo {
        color: #ffffff;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        text-shadow: 2px 2px 8px #000000;
        padding-top: 10px;
    }
    
    .subtitulo {
        color: #f1f1f1;
        text-align: center;
        font-size: 16px;
        margin-bottom: 20px;
        text-shadow: 1px 1px 3px #000000;
    }

    /* Botón verde campero */
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        height: 55px;
        background-color: #2E7D32;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #4CAF50;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    /* Caja de Diagnóstico clara */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2E7D32;
        color: #121212;
        font-size: 16px;
        margin-top: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    /* Estilo para los labels en blanco */
    label {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Diagnóstico experto en tiempo real</div>", unsafe_allow_html=True)

# Selector de origen amigable
opcion = st.radio("Elegí origen:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    foto = st.camera_input("Enfocá la planta")
else:
    foto = st.file_uploader("Subí tu foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 OBTENER INFORME TÉCNICO'):
        with st.spinner('Analizando muestra...'):
            try:
                # Búsqueda automática del modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((600, 600))
                
                prompt = "Como ingeniero agrónomo, analizá esta planta y respondé: 1- Qué problema tiene. 2- Por qué pasó. 3- Cómo tratarlo hoy mismo."
                response = model.generate_content([prompt, img])
                
                # Resultado legible
                st.markdown(f"<div class='reporte-box'><b>✅ DICTAMEN TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error de conexión: {e}")

st.markdown("<br><p style='text-align:center; color:white; font-size:12px;'>© 2026 La Clementina - San Jorge, Santa Fe</p>", unsafe_allow_html=True)
