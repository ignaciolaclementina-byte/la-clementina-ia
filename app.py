import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu API KEY
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

def procesar_y_analizar(archivo_foto):
    img = Image.open(archivo_foto)
    img = img.convert('RGB')
    img.thumbnail((512, 512)) # Para que sea rápido
    
    # CAMBIO CLAVE: Usamos este nombre que no falla
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "Como agrónomo experto, identificá el problema en esta planta y receta tratamiento corto."
    
    response = model.generate_content([prompt, img])
    return response.text

# 2. Interfaz
opcion = st.radio("Elegí origen:", ("Cámara del Celular", "Galería"), horizontal=True)

if opcion == "Cámara del Celular":
    foto = st.camera_input("Sacá la foto")
else:
    foto = st.file_uploader("Subí desde el celu", type=["jpg", "png", "jpeg"])

if foto is not None:
    if st.button('🚀 DIAGNÓSTICO INSTANTÁNEO'):
        with st.spinner('Analizando...'):
            try:
                resultado = procesar_y_analizar(foto)
                st.success("✅ Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                # Si el 1.5 falla, intentamos con el modelo alternativo automáticamente
                try:
                    model_alt = genai.GenerativeModel('gemini-pro-vision')
                    res = model_alt.generate_content(["Diagnóstico corto:", Image.open(foto)])
                    st.success(res.text)
                except:
                    st.error(f"Error: {e}")
