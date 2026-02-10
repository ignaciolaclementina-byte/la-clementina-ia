import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CLAVE NUEVA DIRECTA (Copiada de tu captura image_0404f2.jpg)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="LA CLEMENTINA IA", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. CARGA DE IMAGEN
archivo = st.file_uploader("📸 Subí la foto del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # LA CLAVE: Usamos el nombre del modelo sin el prefijo 'models/'
                # Esto mata el error 404 de tus capturas.
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Sos ingeniero agrónomo. Analizá esta imagen y recomendá: Solomon, Belt, Starkle u Optimizer. Da una dosis breve."
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
