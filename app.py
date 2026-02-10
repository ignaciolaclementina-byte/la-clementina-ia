import streamlit as st
import google.generativeai as genai
from PIL import Image

# CLAVE NUEVA EXTRAÍDA DE TU CAPTURA (image_0404f2.jpg)
# Asegurate de que sea exactamente esta sin espacios al final
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"

genai.configure(api_key=API_KEY)

st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Subir foto", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            # Prompt ultra directo
            response = model.generate_content(["Analizá esta planta y recomendá: Solomon, Belt, Starkle u Optimizer.", img])
            
            if response.text:
                st.success("✅ RECOMENDACIÓN:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error de Google: {str(e)}")
