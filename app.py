import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CLAVE DIRECTA (Para saltar el error de Secrets)
API_KEY = "AIzaSyC250wrUftx2beXB0Tv1KHXlWa9jiTLd2s"
genai.configure(api_key=API_KEY)

# 2. INTERFAZ
st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir imagen de muestra", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando con Google Gemini..."):
            try:
                # Usamos el modelo flash que es el más estable
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Sos un ingeniero agrónomo experto. Analizá la imagen y recomendá tratamiento con: Solomon, Belt, Starkle u Optimizer."
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error: {str(e)}")
