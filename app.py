import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de tu API Key
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- CSS AGRESIVO PARA FONDO DE SOJA ---
st.markdown("""
    <style>
    /* Atacamos el contenedor principal de la App */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

    /* Limpiamos el fondo de la cabecera y el bloque central */
    [data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }

    /* Título principal */
    .titulo-ia {
        color: #C5E1A5;
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        margin-top: -40px;
    }

    /* Estilo para los botones */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #33691E !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid #ffffff !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    /* Caja de Informe (Blanco sólido para que se lea perfecto) */
    .reporte-final {
        background-color: rgba(255, 255, 255, 0.98);
        padding: 25px;
        border-radius: 15px;
        color: #1b5e20;
        font-size: 17px;
        border-left: 10px solid #33691E;
        text-shadow: none !important;
    }

    /* Forzar color de etiquetas de selección */
    label, p, .stMarkdown {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
st.markdown("<div class='titulo-ia'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE IMAGEN:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("SUBIR DESDE CELULAR", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 GENERAR INFORME'):
        with st.spinner('Procesando datos...'):
            try:
                # Lógica del modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                img = Image.open(foto).convert('RGB')
                
                prompt = "Sos un ingeniero agrónomo. Analizá la imagen y da: 1. Diagnóstico, 2. Causa, 3. Tratamiento."
                response = model.generate_content([prompt, img])
                
                st.markdown(f"<div class='reporte-final'><b>📋 RESULTADO TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<br><p style='text-align:center; font-size:10px; opacity:0.7;'>V.4.5 - Optimizado para campo</p>", unsafe_allow_html=True)
