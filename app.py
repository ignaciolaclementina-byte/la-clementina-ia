import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 1. Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS PARA FORZAR SOJA Y QUITAR EL NEGRO
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    [data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }
    .titulo {
        color: white;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px black;
    }
    .informe-caja {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        color: black !important;
        border-left: 10px solid #2E7D32;
    }
    .informe-caja * { color: black !important; }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

# 3. Interfaz
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN:", ["Cámara", "Galería"], horizontal=True)

if opcion == "Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí foto", type=["jpg", "png", "jpeg"])

if archivo:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 OBTENER DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # SOLUCIÓN AL MODELO: Probamos los 3 nombres posibles
                model_name = 'gemini-1.5-flash'
                try:
                    model = genai.GenerativeModel(model_name)
                    img = Image.open(archivo)
                    prompt = "Sos un Ingeniero Agrónomo. Analizá la planta y da: Diagnóstico, Causa y Tratamiento."
                    response = model.generate_content([prompt, img])
                    texto = response.text
                except:
                    # Segundo intento con nombre alternativo
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = model.generate_content([prompt, img])
                    texto = response.text

                # SOLUCIÓN AL SYNTAX ERROR: Sin f-strings con barras
                texto_html = texto.replace("\n", "<br>")
                
                st.markdown(f"""
                <div class='informe-caja'>
                    <strong>📋 INFORME DEL ESPECIALISTA:</strong><br><br>
                    {texto_html}
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Error de conexión. Intentá de nuevo.")
