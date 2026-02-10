import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual (Fondo Soja)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label { color: white !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1>🔐 Acceso</h1>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "clementina2024":
        if st.button("INGRESAR"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. Interfaz
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.camera_input("📸 Sacar foto")
if not archivo:
    archivo = st.file_uploader("📁 O subir archivo", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                # Verificación de Key
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("Error: Falta la clave en Secrets.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # USAMOS EL MODELO MÁS ESTABLE
                model = genai.GenerativeModel(model_name="gemini-1.5-flash")
                
                # Productos de tu Excel
                prompt = (
                    "Sos un experto agrónomo de La Clementina. "
                    "Analizá la imagen y decime qué problema ves. "
                    "Recomendá SOLO estos productos de nuestro stock: "
                    "Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. "
                    "Para mezclas usá: Optimizer, Rizo Spray, Integrum o Zen."
                )
                
                # Generación forzando configuración de seguridad baja para que no se bloquee
                response = model.generate_content(
                    [prompt, img],
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                )
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN:")
                    st.markdown(response.text)
                else:
                    st.error("La IA no devolvió texto. Probá con otra foto.")

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
