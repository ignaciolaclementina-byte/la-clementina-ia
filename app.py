import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual (Fondo Campo)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label { color: white !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Interfaz Principal
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir imagen del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO PROFESIONAL"):
        with st.spinner("Consultando con el motor de La Clementina..."):
            try:
                # CONEXIÓN
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # SOLUCIÓN AL 404: Probamos los nombres de modelo más estables
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                except:
                    model = genai.GenerativeModel('gemini-pro-vision')
                
                prompt = "Actúa como experto agrónomo. Analiza la imagen y da: 1-Diagnóstico, 2-Producto recomendado (Solomon, Starkle, Belt, u Optimizer), 3-Dosis."
                
                # Generar contenido
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ INFORME FINAL:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA no pudo procesar esta imagen. Intenta con otra.")
                    
            except Exception as e:
                st.error(f"Error del servidor: {str(e)}")
