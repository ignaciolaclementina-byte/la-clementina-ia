import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. PEGUÉ TU CLAVE NUEVA ACÁ (La de la imagen image_0404f2.jpg)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"

genai.configure(api_key=API_KEY)

# 2. DISEÑO DE LA APP
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Diagnóstico experto de cultivos</p>", unsafe_allow_html=True)

# 3. CARGA DE IMAGEN
archivo = st.file_uploader("", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Consultando con la IA..."):
            try:
                # Usamos el modelo estable
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = (
                    "Actúa como ingeniero agrónomo de La Clementina. "
                    "Analiza esta imagen de cultivo y recomienda uno de estos productos: "
                    "Solomon, Belt, Starkle u Optimizer. Da una dosis breve."
                )
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.write(response.text)
            except Exception as e:
                st.error(f"Error: {str(e)}")
