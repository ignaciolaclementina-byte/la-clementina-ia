import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la clave
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="LA CLEMENTINA IA")
st.title("🚜 LA CLEMENTINA IA")

# 2. Selector de archivo
archivo = st.file_uploader("📸 Subí la foto", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        try:
            # USAMOS EL NOMBRE DEL MODELO SIN PREFIJOS NI VERSIONES BETA
            # Esto evita el error 404 en entornos Python 3.13
            model = genai.GenerativeModel(model_name='gemini-1.5-flash')
            
            # Pedido directo
            response = model.generate_content([
                "Actuá como ingeniero agrónomo. Analizá la imagen y recomendá tratamiento con Solomon, Belt, Starkle u Optimizer. Sé breve.",
                img
            ])
            
            if response.text:
                st.success("✅ RECOMENDACIÓN TÉCNICA:")
                st.markdown(response.text)
                
        except Exception as e:
            # Si vuelve a dar error, acá nos va a decir exactamente qué versión usa
            st.error(f"Error técnico: {str(e)}")
