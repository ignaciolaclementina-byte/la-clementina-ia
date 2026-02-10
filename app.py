import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración con tu clave
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.title("🚜 La Clementina IA")

def obtener_diagnostico(foto):
    img = Image.open(foto).convert('RGB')
    img.thumbnail((500, 500)) # Compresión para que vuele
    
    # BUSCADOR AUTOMÁTICO DE MODELO (Esto mata el error 404)
    modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_a_usar = modelos_disponibles[0] # Elige el primero que funcione
    
    model = genai.GenerativeModel(modelo_a_usar)
    response = model.generate_content(["Como agrónomo, diagnóstico y tratamiento corto para esta planta.", img])
    return response.text

# Interfaz simple
archivo = st.camera_input("Sacá la foto")
if not archivo:
    archivo = st.file_uploader("O cargala de la galería", type=["jpg", "png", "jpeg"])

if archivo:
    if st.button('🚀 DIAGNÓSTICO YA'):
        with st.spinner('Analizando...'):
            try:
                # Si esto falla es porque el servidor de Streamlit está caído
                res = obtener_diagnostico(archivo)
                st.success(res)
            except Exception as e:
                st.error(f"Error de conexión: {e}. Probá darle de nuevo al botón.")
