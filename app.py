import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 1. Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS para fondo de soja y texto negro
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-attachment: fixed !important;
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
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2E7D32;
        margin-top: 20px;
    }
    .texto-negro {
        color: black !important;
        font-size: 18px;
        font-weight: normal;
    }
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
        with st.spinner("El agrónomo virtual está analizando..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(archivo)
                
                prompt = "Como agrónomo experto, analizá la imagen y da: 1. Diagnóstico, 2. Causa, 3. Tratamiento."
                response = model.generate_content([prompt, img])
                
                # CORRECCIÓN DEFINITIVA: Separamos el texto para evitar SyntaxError
                texto_final = response.text.replace('\n', '<br>')
                
                html_reporte = f"<div class='reporte-blanco'><b style='color: #2E7D32;'>✅ INFORME TÉCNICO:</b><br><br><div class='texto-negro'>{texto_final}</div></div>"
                
                st.markdown(html_reporte, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<br><p style='text-align:center; opacity:0.8; font-size:12px;'>San Jorge, Santa Fe - v6.5</p>", unsafe_allow_html=True)
