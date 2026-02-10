import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CLAVE CORREGIDA Y DIRECTA (Copiada de tu captura image_02ca77.png)
# Asegurate de que no falte la 's' al final
API_KEY = "AIzaSyC250wrUftx2beXB0Tv1KHXlWa9jiTLd2s"

try:
    genai.configure(api_key=API_KEY)
except:
    st.error("Error al configurar la llave de Google.")

# 2. INTERFAZ
st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align:center; color:#4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir imagen del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # Usamos gemini-1.5-flash que es el que acepta esa clave
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Sos ingeniero agrónomo. Analizá esta imagen y recomendá tratamiento con Solomon, Belt, Starkle u Optimizer. Sé breve."
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error de Google: {str(e)}")
                st.info("Si dice API_KEY_INVALID, generá una nueva en Google AI Studio.")
