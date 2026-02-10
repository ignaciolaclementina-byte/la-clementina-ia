import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 1. Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS para fondo de soja y texto negro (Corregido)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed;
    }
    [data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }
    .titulo {
        color: white;
        text-align: center;
        font-size: 35px;
        font-weight: bold;
        text-shadow: 2px 2px 4px black;
    }
    .reporte-blanco {
        background-color: white !important;
        color: black !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2E7D32;
        font-size: 18px;
    }
    .reporte-blanco * { color: black !important; }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

# 3. Interfaz
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.write("---")

opcion = st.radio("ORIGEN DE LA FOTO:", ["Cámara", "Galería"], horizontal=True)

if opcion == "Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí tu imagen", type=["jpg", "png", "jpeg"])

if archivo is not None:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 OBTENER DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # Selección de modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(archivo)
                
                # Prompt y Generación
                prompt = "Como agrónomo, analizá la imagen y da: 1. Diagnóstico, 2. Causa, 3. Tratamiento."
                response = model.generate_content([prompt, img])
                
                # Mostrar resultado con letra negra sobre blanco
                st.markdown(f"""
                <div class='reporte-blanco'>
                    <strong>✅ INFORME TÉCNICO:</strong><br><br>
                    {response.text.replace('\n', '<br>')}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
