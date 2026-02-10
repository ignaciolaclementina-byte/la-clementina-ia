import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- DISEÑO CON FONDO DE CAMPO ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

st.markdown("""
    <style>
    /* Imagen de fondo de soja */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Título y textos */
    .titulo {
        color: #ffffff;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        margin-top: 10px;
    }
    
    .instrucciones {
        color: #e0e0e0;
        text-align: center;
        margin-bottom: 25px;
    }

    /* Botón estilo campero */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 60px;
        background-color: #2E7D32;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #4CAF50;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
    }

    /* Caja de Diagnóstico clara para leer bien */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2E7D32;
        color: #1a1a1a;
        font-size: 16px;
        margin-top: 20px;
    }
    
    /* Estilo para los inputs */
    .stCameraInput > label, .stFileUploader > label {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='instrucciones'>Diagnóstico de precisión en tiempo real</div>", unsafe_allow_html=True)

# Selector de origen
opcion = st.radio("", ["📸 Usar Cámara", "📁 Galería de Fotos"], horizontal=True)

if opcion == "📸 Usar Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Seleccioná la imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 ANALIZAR AHORA'):
        with st.spinner('Consultando con el experto...'):
            try:
                # Detector de modelo automático
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((600, 600))
                
                prompt = "Sos un agrónomo experto. Analizá la imagen y dame: 1. Diagnóstico breve, 2. Causa, 3. Tratamiento sugerido."
                response = model.generate_content([prompt, img])
                
                # Resultado legible
                st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<br><p style='text-align:center; color:white; font-size:12px; font-weight:bold;'>La Clementina - San Jorge, Santa Fe</p>", unsafe_allow_html=True)
