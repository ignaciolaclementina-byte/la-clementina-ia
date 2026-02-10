import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración (Asegurate de que tu API KEY sea la correcta)
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.title("🚜 La Clementina IA")

def get_diagnosis(image):
    # Reducimos la calidad de la imagen para que vuele por internet
    image.thumbnail((800, 800)) 
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt ultra directo para que no pierda tiempo pensando
    prompt = "Respuesta corta: ¿Qué plaga o enfermedad tiene esta planta y cómo se cura?"
    
    response = model.generate_content([prompt, image])
    return response.text

uploaded_file = st.file_uploader("Subí tu foto", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption='Foto cargada', width=300)
    
    if st.button('🚀 DIAGNÓSTICO INSTANTÁNEO'):
        with st.spinner('Procesando...'):
            try:
                # El secreto está en la velocidad
                resultado = get_diagnosis(img)
                st.success("Resultado:")
                st.write(resultado)
            except Exception as e:
                st.error(f"Error: {e}")
