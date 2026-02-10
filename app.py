import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. LA LLAVE ESTÁ ACÁ ADENTRO (Ya no falla el Secret)
API_KEY = "AIzaSyC250wrUftx2beXB0Tv1KHXlWa9jiTLd2s"
genai.configure(api_key=API_KEY)

# 2. INTERFAZ LIMPIA
st.set_page_config(page_title="LA CLEMENTINA IA", layout="centered")
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. SUBIDA DE FOTO
archivo = st.file_uploader("📸 Subir imagen del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, caption="Muestra cargada", use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando con Google Gemini..."):
            try:
                # Usamos el modelo flash sin prefijos raros
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = (
                    "Actúa como ingeniero agrónomo experto de La Clementina. "
                    "Analiza la imagen y recomienda tratamiento con: Solomon, Belt, Starkle u Optimizer."
                )
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA no pudo generar una respuesta clara.")
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
