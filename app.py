import streamlit as st
import google.generativeai as genai
from PIL import Image

# CLAVE DIRECTA (De tu captura image_042056.jpg)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subí la foto", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        try:
            # Esta es la forma que NO da error 404 en Python 3.13
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([
                "Sos ingeniero agrónomo. Analizá la imagen y recomendá tratamiento con Solomon, Belt, Starkle u Optimizer. Sé breve.",
                img
            ])
            if response.text:
                st.success("✅ RECOMENDACIÓN:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error técnico: {str(e)}")
