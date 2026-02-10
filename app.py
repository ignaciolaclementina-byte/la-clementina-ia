import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CLAVE NUEVA (De tu captura image_0404f2.jpg)
# La pongo directo acá para que no dependas de los Secrets
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
            # CAMBIO CLAVE: Quitamos el 'models/' para evitar el error 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Pedido directo
            response = model.generate_content([
                "Sos un ingeniero agrónomo. Mirá la foto y recomendá uno de estos productos: Solomon, Belt, Starkle u Optimizer. Da una dosis técnica.", 
                img
            ])
            
            if response.text:
                st.success("✅ RECOMENDACIÓN TÉCNICA:")
                st.write(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")
