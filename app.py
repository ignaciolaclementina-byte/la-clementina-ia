import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 1. Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS para fondo de soja y lectura clara (Sin errores)
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
    .caja-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2E7D32;
        margin-top: 20px;
    }
    .texto-resultado {
        color: black !important;
        font-size: 18px;
    }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

# 3. Interfaz de Usuario
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.write("---")

opcion = st.radio("ORIGEN DE LA FOTO:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí tu imagen", type=["jpg", "png", "jpeg"])

if archivo is not None:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 OBTENER DIAGNÓSTICO"):
        with st.spinner("Analizando cultivo..."):
            try:
                # Cambiamos a 'gemini-pro-vision' o buscamos el disponible para evitar el error 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(archivo)
                
                prompt = "Actuá como un Ingeniero Agrónomo. Analizá la planta y respondé: 1- Diagnóstico, 2- Causa, 3- Tratamiento."
                response = model.generate_content([prompt, img])
                
                # Procesamos el texto fuera de la f-string para evitar el SyntaxError
                respuesta_texto = response.text.replace("\n", "<br>")
                
                html_final = "<div class='caja-blanca'><b style='color: #2E7D32;'>✅ INFORME TÉCNICO:</b><br><br><div class='texto-resultado'>" + respuesta_texto + "</div></div>"
                
                st.markdown(html_final, unsafe_allow_html=True)
            except Exception as e:
                st.error("Error: " + str(e))

st.markdown("<br><p style='text-align:center; opacity:0.8; font-size:12px;'>San Jorge, Santa Fe - v7.0</p>", unsafe_allow_html=True)
