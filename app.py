import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# CSS REFORZADO - Link nuevo de campo de soja (Unsplash estable)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), 
                    url("https://images.unsplash.com/photo-1594904351111-a072f80b1a71?q=80&w=2070&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
        background-color: #1b3022; /* Color de respaldo si falla la imagen */
    }
    
    .block-container {
        background-color: rgba(0, 0, 0, 0.8); /* Un poco más oscuro para que resalte el texto */
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid #4CAF50;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    h1, h2, h3, p, li, span, label {
        color: white !important;
    }
    
    h1 {
        color: #4CAF50 !important;
        text-align: center;
        font-size: 2.5rem !important;
        text-shadow: 2px 2px 8px #000000;
    }

    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        border: 1px solid #4CAF50;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #45a049;
        border: 1px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Contraseña del sistema:", type="password")
    if st.button("ENTRAR"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta. Intentá de nuevo.")
    st.stop()

# --- MOTOR IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception:
    st.error("Error de conexión. Avisar al técnico.")
    st.stop()

# --- INTERFAZ ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>🌿 <b>Diagnóstico Experto de Cultivos</b></p>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subí la foto aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True, caption="Imagen cargada")
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('⌛ Procesando análisis agronómico...'):
            try:
                prompt = "Sos un ingeniero agrónomo experto. Identificá el cultivo, la enfermedad o plaga y da recomendaciones de tratamiento."
                response = model.generate_content([prompt, img])
                st.success("### ✅ Dictamen:")
                st.markdown(response.text)
            except Exception:
                st.error("❌ Error al analizar la imagen.")
