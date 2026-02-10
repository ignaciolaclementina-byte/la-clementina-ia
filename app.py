import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API configurada
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE INTERFAZ ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# Inyección de CSS para el fondo de soja
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url("https://images.unsplash.com/photo-1559813583-3683a48e718f?auto=format&fit=crop&q=80&w=1600");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .titulo-principal {
        color: #ffffff;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 5px #000000;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 60px;
        background-color: #2E7D32;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #ffffff;
    }

    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2E7D32;
        color: #121212;
        margin-top: 20px;
    }

    label, p {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
st.markdown("<div class='titulo-principal'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)

opcion = st.radio("Elegí origen:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            try:
                # Detección automática de modelo (visto en logs previos)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((600, 600))
                
                prompt = "Como ingeniero agrónomo, analizá la planta y da: Diagnóstico, Causa y Tratamiento corto."
                response = model.generate_content([prompt, img])
                
                # Despliegue del reporte legible
                st.markdown(f"<div class='reporte-box'><b>✅ INFORME TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<p style='text-align:center; font-size:12px;'>Optimizado para San Jorge, Santa Fe</p>", unsafe_allow_html=True)
