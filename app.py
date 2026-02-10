import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu API KEY que es válida
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.title("🚜 La Clementina IA")

def analizar():
    # Achicamos la foto al máximo para que no pese nada
    img = Image.open(foto)
    img = img.convert('RGB')
    img.thumbnail((300, 300))
    
    # USAMOS EL MODELO COMPATIBLE (Esto evita el error 404)
    model = genai.GenerativeModel('gemini-pro-vision')
    
    response = model.generate_content(["Diagnóstico rápido de esta planta y tratamiento.", img])
    return response.text

# 2. Interfaz básica (Cámara o Galería)
opcion = st.radio("Subir:", ("Cámara", "Galería"), horizontal=True)
foto = st.camera_input("Foto") if opcion == "Cámara" else st.file_uploader("Archivo")

if foto:
    if st.button('🚀 DIAGNÓSTICO YA'):
        try:
            with st.spinner('Analizando...'):
                res = analizar()
                st.success(res)
        except Exception as e:
            st.error(f"Error: {e}")
