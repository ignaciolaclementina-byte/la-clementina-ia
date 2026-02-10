import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Tu Clave (Asegurate de pegarla bien)
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.title("🚜 La Clementina IA")

def fast_diagnosis(image_data):
    # COMPRESIÓN ULTRA: Reducimos la foto a un tamaño que vuela por la red
    img = Image.open(image_data)
    img = img.convert('RGB')
    img.thumbnail((300, 300)) # Tamaño mínimo para análisis rápido
    
    # Modelo optimizado para velocidad
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt corto = Procesamiento rápido
    prompt = "Respuesta de agrónomo en 2 renglones: ¿Qué tiene y qué aplico?"
    
    response = model.generate_content([prompt, img])
    return response.text

# 2. Interfaz rápida
opcion = st.radio("Origen:", ("Cámara", "Galería"))
foto = st.camera_input("Sacá la foto") if opcion == "Cámara" else st.file_uploader("Subí foto", type=["jpg", "png"])

if foto:
    if st.button('🚀 ANALIZAR AHORA'):
        # Usamos un mensaje simple para no gastar recursos
        st.write("⏳ Procesando en segundos...")
        try:
            resultado = fast_diagnosis(foto)
            st.success(resultado)
        except Exception as e:
            st.error("Error de conexión. Reintentá.")
