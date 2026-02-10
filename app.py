import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Tu Clave (Reemplazala entre las comillas)
API_KEY = "TU_API_KEY_AQUÍ"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="La Clementina IA", layout="centered")
st.title("🚜 La Clementina IA")

# 2. Configuración para que responda RÁPIDO
def get_diagnosis(image):
    # Forzamos una respuesta corta y directa para ganar velocidad
    model = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # Configuramos la IA para que no de vueltas
    config = genai.types.GenerationConfig(
        candidate_count=1,
        stop_sequences=['x'],
        max_output_tokens=500, # Respuesta corta = respuesta rápida
        temperature=0.4, # Menos "creatividad" para que no dude
    )
    
    prompt = "Analizá rápido esta planta. Identificá el problema y dame una solución corta en 3 puntos."
    
    # Enviamos la imagen
    response = model.generate_content([prompt, image], generation_config=config)
    return response.text

# 3. La Interfaz (Lo que ya te funcionaba)
uploaded_file = st.file_uploader("Subí la foto del cultivo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Imagen cargada', use_column_width=True)
    
    if st.button('🚀 INICIAR DIAGNÓSTICO'):
        # Usamos una barra de progreso para que sepas que está trabajando
        progress_bar = st.progress(0)
        with st.spinner('Conectando con el experto...'):
            try:
                progress_bar.progress(50)
                resultado = get_diagnosis(image)
                progress_bar.progress(100)
                st.success("✅ Diagnóstico:")
                st.write(resultado)
            except Exception as e:
                st.error(f"Se agotó el tiempo: {e}")
