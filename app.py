import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual (Fondo Soja Atardecer)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; font-weight: bold; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 Acceso</h1>", unsafe_allow_html=True)
    if st.text_input("Contraseña:", type="password") == "clementina2024":
        if st.button("INGRESAR"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. Interfaz Principal
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.camera_input("📸 Tomar foto")
if not archivo:
    archivo = st.file_uploader("📁 O subir archivo", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando..."):
            try:
                # Verificación de Key
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("Error: Falta la GOOGLE_API_KEY en Secrets.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Productos del Excel 2026
                productos = "Insecticidas: Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. Adherentes: Optimizer, Rizo Spray, Integrum, Fulltec, Zen."
                
                prompt = f"Sos ingeniero agrónomo de La Clementina. Identificá el problema en la foto y recomendá tratamiento con estos productos: {productos}."
                
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN:")
                    st.markdown(response.text)
                else:
                    st.error("La IA no pudo procesar la imagen.")
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
