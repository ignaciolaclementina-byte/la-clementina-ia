import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de API (Directa y limpia)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clave en Secrets")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Interfaz
st.set_page_config(page_title="LA CLEMENTINA IA")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir imagen", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 GENERAR DIAGNÓSTICO YA"):
        with st.spinner("Conectando con Google..."):
            try:
                # LA SOLUCIÓN AL 404: Usar el nombre corto sin prefijos
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Actúa como experto agrónomo de La Clementina. Analiza la imagen y da: 1-Diagnóstico, 2-Producto (Solomon, Starkle, Belt, u Optimizer), 3-Dosis."
                
                # Enviar como lista simple
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RESULTADO:")
                    st.markdown(response.text)
                else:
                    st.error("La IA no pudo procesar esta imagen.")
            except Exception as e:
                st.error(f"Error crítico: {str(e)}")
                st.info("Hacé un 'Reboot' en el panel de Streamlit si el error persiste.")
