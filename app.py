import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

def analizar_foto(foto):
    img = Image.open(foto)
    img = img.convert('RGB')
    img.thumbnail((500, 500))
    
    # Motor de búsqueda de modelos: busca el que esté disponible
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    response = model.generate_content(["Diagnóstico rápido de este cultivo y qué aplicar.", img])
    return response.text

# 2. Interfaz
opcion = st.radio("Elegí:", ("Cámara", "Galería"), horizontal=True)
archivo = st.camera_input("Foto") if opcion == "Cámara" else st.file_uploader("Subir", type=["jpg", "png", "jpeg"])

if archivo:
    if st.button('🚀 DIAGNÓSTICO YA'):
        with st.spinner('Analizando...'):
            try:
                res = analizar_foto(archivo)
                st.success(res)
            except Exception as e:
                # Si el 1.5 falla, intentamos con el 1.0 por si la cuenta es vieja
                try:
                    model_alt = genai.GenerativeModel('gemini-1.0-pro-vision-latest')
                    res_alt = model_alt.generate_content(["Diagnóstico:", Image.open(archivo)])
                    st.success(res_alt.text)
                except:
                    st.error(f"Error de sistema: {e}")
