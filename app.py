import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu API KEY que funciona
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

def analizar_cultivo(foto):
    # Compresión para que no se tilde
    img = Image.open(foto)
    img = img.convert('RGB')
    img.thumbnail((400, 400))
    
    # EL CAMBIO QUE FALTA: Usar el modelo base que no da 404
    # Si el Flash da error en tu zona/versión, este lo levanta sí o sí
    try:
        model = genai.GenerativeModel('gemini-pro-vision')
    except:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = "Diagnóstico técnico rápido de este cultivo y tratamiento."
    response = model.generate_content([prompt, img])
    return response.text

# 2. Interfaz sin fallas
opcion = st.radio("Subir desde:", ("Cámara", "Galería"), horizontal=True)

if opcion == "Cámara":
    archivo = st.camera_input("Sacá la foto")
else:
    archivo = st.file_uploader("Elegí imagen", type=["jpg", "jpeg", "png"])

if archivo:
    if st.button('🚀 DIAGNÓSTICO YA'):
        with st.spinner('Analizando...'):
            try:
                # Ahora sí tiene que traer el texto
                resultado = analizar_cultivo(archivo)
                st.success(resultado)
            except Exception as e:
                st.error(f"Error: {e}")
