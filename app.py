import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 1. Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS para fondo de soja y lectura clara
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
        font-size: 32px;
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
    .texto-negro {
        color: black !important;
        font-size: 18px;
    }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

# 3. Interfaz
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA FOTO:", ["Cámara", "Galería"], horizontal=True)

if opcion == "Cámara":
    archivo = st.camera_input("")
else:
    archivo = st.file_uploader("Subí tu imagen", type=["jpg", "png", "jpeg"])

if archivo is not None:
    st.image(archivo, use_container_width=True)
    
    if st.button("🚀 OBTENER DIAGNÓSTICO"):
        with st.spinner("Analizando cultivo..."):
            try:
                # SOLUCIÓN AL ERROR 404: Buscamos el modelo dinámicamente
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                img = Image.open(archivo)
                
                prompt = "Actuá como un Ingeniero Agrónomo. Analizá la planta y respondé: 1- Diagnóstico, 2- Causa, 3- Tratamiento."
                response = model.generate_content([prompt, img])
                
                # SOLUCIÓN AL SYNTAX ERROR: Sin f-strings con barras invertidas
                res_text = response.text.replace("\n", "<br>")
                
                informe_html = "<div class='caja-blanca'><b style='color: #2E7D32;'>✅ INFORME TÉCNICO:</b><br><br><div class='texto-negro'>" + res_text + "</div></div>"
                
                st.markdown(informe_html, unsafe_allow_html=True)
            except Exception as e:
                # Si falla el anterior, probamos el modelo alternativo
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content([prompt, img])
                    res_text = response.text.replace("\n", "<br>")
                    st.markdown("<div class='caja-blanca'><div class='texto-negro'>" + res_text + "</div></div>", unsafe_allow_html=True)
                except:
                    st.error("Error de conexión con el modelo. Reintentá en un momento.")

st.markdown("<br><p style='text-align:center; opacity:0.8; font-size:12px;'>v8.0 - Estable</p>", unsafe_allow_html=True)
