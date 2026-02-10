import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- CSS PARA FORZAR FONDO DE SOJA Y TEXTO NEGRO ---
st.markdown("""
    <style>
    /* 1. Fondo de soja: Eliminamos el fondo negro de Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        background-repeat: no-repeat !important;
    }

    /* Transparencia para capas intermedias */
    [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }

    /* 2. Caja de Informe: Texto Negro sobre Blanco Puro */
    .caja-blanca {
        background-color: #ffffff !important;
        padding: 25px;
        border-radius: 15px;
        color: #000000 !important;
        font-size: 18px;
        line-height: 1.6;
        border-left: 15px solid #2E7D32;
        margin-top: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.8);
    }
    
    .caja-blanca h3, .caja-blanca b, .caja-blanca p, .caja-blanca div {
        color: #000000 !important;
    }

    /* 3. Estilo de Títulos y Botones */
    .titulo-principal {
        color: #ffffff;
        text-align: center;
        font-size: 34px;
        font-weight: bold;
        text-shadow: 2px 2px 5px #000000;
        margin-top: -50px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid #ffffff !important;
    }

    /* Labels en blanco para que se vean sobre la soja */
    label, p, .stMarkdown {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 3px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
st.markdown("<div class='titulo-principal'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
opcion = st.radio("ORIGEN DE LA IMAGEN:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    archivo = st.camera_input("")
else:
    # Corregido: Corchete cerrado correctamente
    archivo = st.file_uploader("SUBIR FOTO DEL LOTE", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO TÉCNICO'):
        with st.spinner('Analizando muestra...'):
            try:
                # Inicialización del modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(archivo).convert('RGB')
                
                prompt = "Actuá como un Ingeniero Agrónomo experto. Analizá la imagen y dame: 1. Diagnóstico, 2. Causa probable, 3. Tratamiento sugerido."
                response = model.generate_content([prompt, img])
