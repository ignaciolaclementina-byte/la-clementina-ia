import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual
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
        with st.spinner("Conectando con el motor de IA..."):
            try:
                # CONFIGURACIÓN DE API
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # ESTRATEGIA PARA EVITAR EL ERROR 404
                # Intentamos diferentes nombres de modelo hasta que uno responda
                model_names = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro-vision']
                model = None
                
                for name in model_names:
                    try:
                        temp_model = genai.GenerativeModel(name)
                        # Prueba rápida de conexión
                        model = temp_model
                        break 
                    except:
                        continue
                
                if model is None:
                    st.error("No se pudo establecer conexión con ningún modelo compatible.")
                    st.stop()

                prompt = "Actúa como experto agrónomo de La Clementina. Analiza la imagen y da: 1-Diagnóstico, 2-Producto recomendado (Solomon, Starkle, Belt, u Optimizer), 3-Dosis."
                
                # Generar contenido
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ INFORME FINAL:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA recibió la imagen pero no pudo generar un texto. Intenta con otra toma.")
                    
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
                st.info("Tip: Si el error persiste, realiza un 'Reboot' en el menú lateral de Streamlit Cloud.")
