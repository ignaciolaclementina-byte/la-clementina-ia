import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de la API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Error: Cargá la clave en los Secrets de Streamlit.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Interfaz limpia
st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir imagen", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Conectando con Google..."):
            try:
                # LLAMADA DIRECTA (Sin prefijos que causen 404)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Sos ingeniero agrónomo. Analizá esta imagen y recomendá tratamiento con Solomon, Belt, Starkle u Optimizer."
                
                # Enviamos la imagen directamente
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN:")
                    st.write(response.text)
            except Exception as e:
                # Si falla, te damos el error exacto para liquidarlo
                st.error(f"Error técnico: {str(e)}")
