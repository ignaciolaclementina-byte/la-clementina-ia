import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu API KEY ya integrada para que no tengas que tocar nada
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")
st.write("Diagnóstico de cultivos al instante.")

# 2. Función optimizada para máxima velocidad
def get_diagnosis(image_data):
    # Achicamos la foto para que el análisis sea un rayo
    img = Image.open(image_data)
    img = img.convert('RGB')
    img.thumbnail((400, 400))
    
    # Usamos Gemini 1.5 Flash (el más rápido de Google)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Orden directa para respuesta inmediata
    prompt = "Respuesta corta de agrónomo: ¿Qué problema tiene la planta y qué producto o acción aplicar? Máximo 3 renglones."
    
    response = model.generate_content([prompt, img])
    return response.text

# 3. Opciones: Cámara o Galería
opcion = st.radio("¿Cómo querés subir la foto?", ("Cámara del Celular", "Galería de Fotos"))

if opcion == "Cámara del Celular":
    archivo = st.camera_input("Sacá la foto a la hoja o planta")
else:
    archivo = st.file_uploader("Elegí una imagen", type=["jpg", "jpeg", "png"])

# 4. Botón de acción
if archivo:
    if st.button('🚀 INICIAR DIAGNÓSTICO'):
        with st.spinner('La Clementina está analizando...'):
            try:
                # Ahora con la clave puesta, esto vuela
                resultado = get_diagnosis(archivo)
                st.success("✅ Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                st.error(f"Error técnico: {e}")
                st.info("Si el error persiste, probá sacar la foto de nuevo.")
