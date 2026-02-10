import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# CSS actualizado con link de imagen nuevo
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1589923188900-85dae523342b?auto=format&fit=crop&q=80&w=2070");
        background-attachment: fixed;
        background-size: cover;
    }
    
    .block-container {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #2e7d32;
        margin-top: 2rem;
    }

    h1, h2, h3, p, li, .stMarkdown {
        color: white !important;
    }
    
    h1 {
        color: #4CAF50 !important;
        text-align: center;
        text-shadow: 2px 2px 4px #000000;
    }

    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border-radius: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Ingresá la contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- CONFIGURACIÓN IA (INTELIGENTE) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception as e:
    st.error(f"Error de conexión. Avisar al administrador.")
    st.stop()

# --- INTERFAZ ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
archivo = st.file_uploader("📸 Cargar imagen aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    if st.button("🚀 INICIAR DIAGNÓSTICO PROFESIONAL"):
        with st.spinner('Analizando...'):
            try:
                prompt = "Sos un ingeniero agrónomo experto. Identifica el cultivo, el problema y da un tratamiento con productos y dosis."
                response = model.generate_content([prompt, img])
                st.success("### ✅ Dictamen:")
                st.write(response.text)
            except Exception as e:
                st.error("❌ Error al procesar.")
