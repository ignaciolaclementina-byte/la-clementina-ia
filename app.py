import streamlit as st
import google.generativeai as genai
from PIL import Image

# CLAVE NUEVA (De tu captura image_042056.jpg)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="LA CLEMENTINA IA")
st.title("🚜 LA CLEMENTINA IA")

archivo = st.file_uploader("📸 Subí la foto", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img)
    
    if st.button("🚀 ANALIZAR"):
        try:
            # Esta línea es la que mata el error 404
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            response = model.generate_content([
                "Sos ingeniero agrónomo. Analizá la imagen y recomendá: Solomon, Belt, Starkle u Optimizer.",
                img
            ])
            
            st.success("✅ RECOMENDACIÓN:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Error: {str(e)}")
