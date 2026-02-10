import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de tu API Key (La que ya funciona)
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE INTERFAZ CAMPERA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

st.markdown("""
    <style>
    /* Imagen de fondo de soja con capa protectora para leer bien */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                    url("https://images.unsplash.com/photo-1559813583-3683a48e718f?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Título principal */
    .titulo-principal {
        color: #ffffff;
        text-align: center;
        font-size: 35px;
        font-weight: bold;
        text-shadow: 3px 3px 6px #000000;
        margin-bottom: 5px;
    }
    
    .subtitulo {
        color: #f1f1f1;
        text-align: center;
        font-size: 18px;
        text-shadow: 1px 1px 3px #000000;
        margin-bottom: 25px;
    }

    /* Botón de acción grande */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 60px;
        background-color: #2E7D32;
        color: white;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #ffffff;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Tarjeta de Reporte (Blanco sólido para lectura) */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        border-left: 10px solid #2E7D32;
        color: #121212;
        font-size: 17px;
        margin-top: 25px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.4);
    }

    /* Color de los textos de carga */
    label, p {
        color: white !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("<div class='titulo-principal'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Diagnóstico de Precisión - San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# Selección de entrada
opcion = st.radio("Elegí cómo cargar la imagen:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí la foto del cultivo", type=["jpg", "png", "jpeg"])

if archivo:
    # Mostramos la muestra cargada
    st.image(archivo, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Consultando con el agrónomo virtual...'):
            try:
                # Sistema de detección automática de modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(archivo).convert('RGB')
                img.thumbnail((700, 700))
                
                prompt = "Actuá como un Ingeniero Agrónomo experto. Analizá la planta y proporcioná: 1. Diagnóstico, 2. Causa probable, 3. Tratamiento recomendado."
                response = model.generate_content([prompt, img])
                
                # Despliegue del reporte
                st.markdown(f"<div class='reporte-box'><b>✅ INFORME TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error en el sistema: {e}")

st.markdown("<br><p style='text-align:center; font-size:12px;'>V.3.5 - Optimizado para el campo</p>", unsafe_allow_html=True)
