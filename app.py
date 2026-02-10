import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Tu API KEY (Ya integrada)
API_KEY = "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

def procesar_y_analizar(archivo_foto):
    # COMPRESIÓN AGRESIVA: Para que no tarde nada
    img = Image.open(archivo_foto)
    img = img.convert('RGB')
    
    # Si la foto es gigante, la bajamos a un tamaño web estándar
    img.thumbnail((512, 512))
    
    # Usamos el modelo más rápido
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt corto y seco
    prompt = "Como agrónomo, identificá el problema en esta planta y receta tratamiento. Máximo 3 renglones."
    
    response = model.generate_content([prompt, img])
    return response.text

# 2. Interfaz Limpia
opcion = st.radio("Elegí origen:", ("Cámara del Celular", "Galería"), horizontal=True)

if opcion == "Cámara del Celular":
    foto = st.camera_input("Sacá la foto")
else:
    foto = st.file_uploader("Subí desde el celu", type=["jpg", "png", "jpeg"])

# 3. Ejecución
if foto is not None:
    if st.button('🚀 DIAGNÓSTICO INSTANTÁNEO'):
        with st.spinner('Analizando...'):
            try:
                # El proceso ahora es liviano, debería tardar 4-5 segundos
                resultado = procesar_y_analizar(foto)
                st.success("✅ Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                # Si hay error, te lo va a decir claro acá
                st.error(f"Hubo un problema: {e}")
