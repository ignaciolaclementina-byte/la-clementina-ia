import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- DISEÑO DE INTERFAZ (CSS) ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# CORRECCIÓN AQUÍ: unsafe_allow_html=True
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f1;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border: none;
    }
    h1 {
        color: #1b5e20;
        text-align: center;
    }
    .diagnostico-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2e7d32;
        color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Asistente Inteligente para Diagnóstico de Cultivos</p>", unsafe_allow_html=True)

def obtener_diagnostico(foto):
    img = Image.open(foto).convert('RGB')
    img.thumbnail((500, 500))
    
    # Usamos el buscador automático que ya probamos que funciona
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(modelos[0])
    
    prompt = "Como agrónomo experto, analizá la imagen. 1- Diagnóstico, 2- Causa, 3- Tratamiento corto."
    response = model.generate_content([prompt, img])
    return response.text

# Interfaz
archivo = st.camera_input("Sacá la foto")
if not archivo:
    archivo = st.file_uploader("O cargá de galería", type=["jpg", "png", "jpeg"])

if archivo:
    if st.button('🚀 INICIAR ANÁLISIS'):
        with st.spinner('Analizando...'):
            try:
                res = obtener_diagnostico(archivo)
                st.markdown(f"<div class='diagnostico-box'>{res}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
