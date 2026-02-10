import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# --- ESTILOS CSS (FONDO CAMPO DE SOJA) ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2232&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #4CAF50;
    }
    h1, h2, h3, p, li, label, .stMarkdown, span {
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
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Contrasena:", type="password")
    if st.button("ENTRAR"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- MOTOR IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception:
    st.error("Error de conexion con la IA")
    st.stop()

# --- INTERFAZ ---
st.markdown("<h1>LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.write("Diagnostico Experto de Cultivos")

archivo = st.file_uploader("Cargar foto aqui:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("INICIAR DIAGNOSTICO"):
        with st.spinner('Analizando...'):
            try:
                # Prompt simple para evitar errores de comillas
                texto_pedido = "Sos un ingeniero agronomo. Identifica el cultivo y la enfermedad en la foto. Da tratamiento y dosis."
                res = model.generate_content([texto_pedido, img])
                st.success("Dictamen Tecnico:")
                st.write(res.text)
            except Exception as e:
                st.error("Error al procesar la imagen")
