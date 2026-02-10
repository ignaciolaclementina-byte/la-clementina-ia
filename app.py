import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración (Pegá tu clave acá)
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

# 2. Función de análisis directo
def analizar_planta(foto):
    # COMPRESIÓN: Reducimos la foto al mínimo para que no tarde nada
    img = Image.open(foto)
    img = img.convert('RGB')
    img.thumbnail((300, 300)) # Tamaño ultra-liviano
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt corto para que la IA responda al toque
    prompt = "Respuesta corta y técnica: ¿Qué tiene la planta y qué producto aplicar?"
    
    response = model.generate_content([prompt, img])
    return response.text

# 3. Interfaz con Cámara
opcion = st.radio("Origen de la foto:", ("Cámara del Celular", "Galería"))

if opcion == "Cámara del Celular":
    archivo = st.camera_input("Sacá la foto a la planta")
else:
    archivo = st.file_uploader("Subí desde galería", type=["jpg", "png", "jpeg"])

if archivo:
    if st.button('🚀 DIAGNÓSTICO YA'):
        with st.spinner('Analizando...'):
            try:
                # El secreto: proceso liviano
                resultado = analizar_planta(archivo)
                st.success("✅ Resultado:")
                st.write(resultado)
            except Exception as e:
                st.error("Servidor ocupado. Probá de nuevo en 5 segundos.")
