import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

st.title("🚜 LA CLEMENTINA IA")

archivo = st.file_uploader("📸 Subir imagen", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img)
    
    if st.button("🚀 ANALIZAR"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(["Diagnóstico y producto: Solomon, Belt o Starkle?", img])
        st.success(response.text)
