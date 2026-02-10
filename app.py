import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu Clave (Asegurate de que sea la correcta)
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.title("🚜 La Clementina IA")

# 2. Función de diagnóstico optimizada para VELOCIDAD
def get_diagnosis(image):
    # Achicamos la imagen drásticamente para que viaje rápido
    img = Image.open(image)
    img.thumbnail((400, 400)) # Tamaño pequeño = Análisis veloz
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Orden ultra-directa
    prompt = "Respuesta de 1 párrafo: ¿Qué problema tiene la planta y qué producto aplicar?"
    
    response = model.generate_content([prompt, img])
    return response.text

# 3. Interfaz con Cámara
opcion = st.radio("Seleccioná origen:", ("Cámara del Celular", "Galería de Fotos"))

foto = None
if opcion == "Cámara del Celular":
    foto = st.camera_input("Sacá la foto")
else:
    foto = st.file_uploader("Elegí imagen", type=["jpg", "jpeg", "png"])

if foto is not None:
    if st.button('🚀 DIAGNÓSTICO YA'):
        with st.spinner('Analizando...'):
            try:
                # Esto ahora debería tardar menos de 5 segundos
                resultado = get_diagnosis(foto)
                st.success("Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                st.error(f"Error: {e}")
