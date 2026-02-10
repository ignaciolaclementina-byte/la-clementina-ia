import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# CSS CON IMAGEN DE FONDO ESTABLE (Campo de Soja al Atardecer)
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2232&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }
    
    /* Contenedor del contenido (Fondo oscuro transparente) */
    .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #4CAF50;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    /* Textos en blanco */
    h1, h2, h3, p, li, label, .stMarkdown {
        color: white !important;
    }
    
    /* Título Principal */
    h1 {
        color: #4CAF50 !important;
        text-align: center;
        font-size: 3rem !important;
        text-shadow: 2px 2px 4px #000000;
        font-weight: 800;
    }

    /* Botón Personalizado */
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border: none;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
        transform: scale(1.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Ingresá la contraseña:", type="password")
    if st.button("INGRESAR AL SISTEMA"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("🔒 Clave incorrecta")
    st.stop()

# --- CONFIGURACIÓN MOTOR IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Buscador inteligente de modelo
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception:
    st.error("⚠️ Error de conexión con el servidor IA.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Diagnóstico Experto de Cultivos</h3>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subí la foto de la planta afectada:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    st.markdown("---")
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('⌛ El ingeniero IA está analizando la muestra...'):
            try:
                prompt = "Actúa como un ingeniero agrónomo senior. Analiza esta imagen. 1. Identifica el cultivo. 2. Diagnostica el problema (plaga, enfermedad, deficiencia). 3. Recomienda tratamiento
