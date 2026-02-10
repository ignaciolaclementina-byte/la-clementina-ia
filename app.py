import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave real
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.title("🚜 La Clementina IA")

def analizar(foto_archivo):
    img = Image.open(foto_archivo).convert('RGB')
    img.thumbnail((500, 500))
    
    # INTENTO 1: El modelo más nuevo con ruta completa
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(["Diagnóstico y tratamiento corto.", img])
        return response.text
    except:
        # INTENTO 2: El modelo anterior por si el servidor es viejo
        model = genai.GenerativeModel('models/gemini-pro-vision')
        response = model.generate_content(["Diagnóstico y tratamiento corto.", img])
        return response.text

# Interfaz con Cámara y Galería
archivo = st.camera_input("Sacá la foto")
if not archivo:
    archivo = st.file_uploader("O subí un archivo", type=["jpg", "png", "jpeg"])

if archivo:
    if st.button('🚀 DIAGNÓSTICO YA'):
        try:
            with st.spinner('Analizando...'):
                resultado = analizar(archivo)
                st.success(resultado)
        except Exception as e:
            st.error(f"Error crítico: {e}")
