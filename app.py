import streamlit as st
import google.generativeai as genai
from PIL import Image

# CLAVE NUEVA (Captura image_0404f2.jpg)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center; color: white;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subí la foto del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        try:
            # EL CAMBIO CLAVE: Quitamos el prefijo 'models/' que te está dando el 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Pedido directo
            response = model.generate_content([
                "Actuá como ingeniero agrónomo. Analizá la imagen y recomendá tratamiento con Solomon, Belt, Starkle u Optimizer. Da una dosis.",
                img
            ])
            
            if response.text:
                st.success("✅ RECOMENDACIÓN TÉCNICA:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error técnico: {str(e)}")
