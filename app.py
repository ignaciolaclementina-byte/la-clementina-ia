import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# CSS personalizado para el fondo de soja y texto blanco
st.markdown("""
    <style>
    /* Fondo de campo de soja */
    .stApp {
        background-image: url("https://i.imgur.com/FnYw5kH.jpeg"); /* Imagen de campo al atardecer */
        background-attachment: fixed;
        background-size: cover;
    }
    
    /* Contenedor principal semi-transparente oscuro para que se lea el texto */
    .block-container {
        background-color: rgba(0, 0, 0, 0.75);
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #2e7d32; /* Borde verde campo */
        margin-top: 2rem;
    }

    /* Texto en blanco para contraste */
    h1, h2, h3, p, li, .stMarkdown {
        color: white !important;
    }
    
    /* Títulos principales en verde "Clementina" */
    h1 {
        color: #4CAF50 !important;
        text-align: center;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
    }

    /* Botón verde personalizado */
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border-radius: 15px;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
    }
    
    /* Ajuste de los cuadros de mensaje */
    .stSuccess, .stError, .stInfo {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1 style='color: white;'>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
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
    # Buscador automático del mejor modelo disponible
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception as e:
    st.error(f"Error de conexión con el motor de IA. Avisar al administrador.")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
# Título con ícono de tractor
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.write("### 🌾 Diagnóstico Experto para tus Cultivos")
st.write("Subí una foto clara de la planta afectada para recibir un análisis profesional al instante.")

archivo = st.file_uploader("📸 Cargar imagen aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    # Mostrar imagen con bordes redondeados
    st.image(img, use_container_width=True)
    
    st.write("---") # Separador
    
    if st.button("🚀 INICIAR DIAGNÓSTICO PROFESIONAL"):
        with st.spinner('⌛ El ingeniero IA está analizando la imagen...'):
            try:
                prompt = "Sos un ingeniero agrónomo experto. Analizá esta imagen de cultivo detalladamente. Identificá el cultivo, el problema específico (plaga, enfermedad, deficiencia) y recomendá un tratamiento claro con productos y dosis si aplica. Sé conciso y profesional."
                response = model.generate_content([prompt, img])
                
                st.success("### ✅ Dictamen Técnico Finalizado")
                st.write(response.text)
                st.write("---")
                st.info("💡 Nota: Este diagnóstico es una herramienta de asistencia basada en inteligencia artificial.")
            except Exception as e:
                st.error("❌ No se pudo completar el análisis. Por favor, intentá con otra foto más clara.")
