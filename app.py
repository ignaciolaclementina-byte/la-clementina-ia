import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la API (Asegurate de que tu API KEY esté entre las comillas)
API_KEY = "TU_API_KEY_AQUÍ"
genai.configure(api_key=API_KEY)

# Configuración de página
st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")
st.write("Subí una foto de tu cultivo para recibir un diagnóstico agronómico.")

# 2. Función de diagnóstico con filtros desactivados para evitar bloqueos
def get_diagnosis(image):
    # Usamos la ruta completa al modelo
    model = genai.GenerativeModel(
        model_name='models/gemini-1.5-flash',
        generation_config={"temperature": 0.7, "top_p": 0.95, "max_output_tokens": 1000},
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )
    
    prompt = (
        "Actuá como un experto ingeniero agrónomo de Argentina. "
        "Analizá detalladamente esta imagen de un cultivo. "
        "Si ves alguna plaga, hongo o deficiencia nutricional, identificala. "
        "Dá una recomendación técnica para el tratamiento. "
        "Si la imagen no es clara, pedí otra foto pero intentá dar una primera impresión."
    )
    
    response = model.generate_content([prompt, image])
    return response.text

# 3. Interfaz de usuario
uploaded_file = st.file_uploader("Seleccionar imagen...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagen cargada para análisis', use_column_width=True)
    
    if st.button('🚀 INICIAR DIAGNÓSTICO'):
        with st.spinner('La Clementina está analizando tu cultivo...'):
            try:
                # Llamada a la IA
                resultado = get_diagnosis(image)
                st.success("✅ Diagnóstico Completado:")
                st.markdown(resultado)
            except Exception as e:
                st.error(f"Hubo un problema al conectar con el experto: {e}")
                st.info("Revisá que tu API KEY sea correcta y que tengas conexión a internet.")
