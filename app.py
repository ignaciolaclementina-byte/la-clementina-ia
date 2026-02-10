import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuración de API (Poné tu clave acá)
genai.configure(api_key="TU_API_KEY_AQUÍ")

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

def get_diagnosis(image):
    # REDUCCIÓN DE TAMAÑO: El secreto de la velocidad
    img = Image.open(image)
    img.thumbnail((500, 500)) # La hacemos chiquita para que viaje rápido
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt ultra-corto para respuesta inmediata
    prompt = "Respuesta técnica rápida: ¿Qué plaga/enfermedad tiene y cómo se cura? Máximo 3 renglones."
    
    response = model.generate_content([prompt, img])
    return response.text

# 2. OPCIONES DE CARGA (Cámara + Archivo)
opcion = st.radio("¿Cómo querés subir la foto?", ("Usar Cámara del Celular", "Subir Archivo de la Galería"))

foto = None
if opcion == "Usar Cámara del Celular":
    foto = st.camera_input("Sacá la foto a la planta")
else:
    foto = st.file_uploader("Elegí una imagen", type=["jpg", "jpeg", "png"])

# 3. EJECUCIÓN
if foto is not None:
    if st.button('🚀 DIAGNÓSTICO AL INSTANTE'):
        with st.spinner('Analizando...'):
            try:
                # El proceso ahora es mucho más liviano
                resultado = get_diagnosis(foto)
                st.success("Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                st.error(f"Error: {e}. Probá sacar la foto de más lejos.")
