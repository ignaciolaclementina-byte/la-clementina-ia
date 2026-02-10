import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración - PONÉ TU API KEY ACÁ
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")
st.write("Carga una foto para analizar el cultivo.")

# 2. Selector de archivos
uploaded_file = st.file_uploader("Subir imagen...", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen cargada", use_column_width=True)
    
    if st.button("🔍 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # El truco: 'models/' adelante del nombre
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                response = model.generate_content(["Analizá esta planta y decime qué enfermedad tiene y cómo tratarla.", image])
                st.success("Diagnóstico:")
                st.write(response.text)
            except Exception as e:
                st.error(f"Error técnico: {e}")
