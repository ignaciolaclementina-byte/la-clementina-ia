import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CONFIGURACIÓN DE SEGURIDAD
# Define aquí tu contraseña (luego podrás cambiarla)
PASSWORD_CORRECTA = "clementina2024" 

def check_password():
    """Devuelve True si el usuario ingresó la contraseña correcta."""
    if "password_ok" not in st.session_state:
        st.session_state["password_ok"] = False

    if st.session_state["password_ok"]:
        return True

    st.markdown("<h1 style='text-align: center;'>🔐 Acceso Restringido</h1>", unsafe_allow_html=True)
    password = st.text_input("Introduce la contraseña de La Clementina:", type="password")
    
    if st.button("Ingresar"):
        if password == PASSWORD_CORRECTA:
            st.session_state["password_ok"] = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    return False

# Solo si la contraseña es correcta, mostramos la App
if check_password():

    # --- CONFIGURACIÓN DE LA PÁGINA ---
    st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

    # Recuperamos la llave de forma segura desde los Secrets de Streamlit
    # Asegúrate de configurar GOOGLE_API_KEY en los Secrets de Streamlit Cloud
    try:
        GOOGLE_KEY = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=GOOGLE_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        st.error("Falta configurar la API KEY en los Secrets del servidor.")
        st.stop()

    # --- ESTILO VISUAL LC AGRO ---
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; }
        [data-testid="stFileUploadDropzone"] {
            background-color: #ffffff !important;
            border: 2px dashed #1b5e20 !important;
        }
        h1 { color: #1b5e20 !important; text-align: center; font-weight: 800; }
        .stButton>button {
            background-color: #1b5e20 !important;
            color: white !important;
            width: 100%;
            border-radius: 10px;
            font-weight: bold;
            height: 3em;
        }
        .resultado-card {
            background-color: #f9fbf9;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #1b5e20;
            color: #000000 !important;
        }
        p, li, span, label { color: #000000 !important; }
        </style>
        """, unsafe_allow_html=True)

    st.title("🚜 LA CLEMENTINA IA")
    st.markdown("<p style='text-align: center; color: #4caf50 !important;'>Innovación para el Campo</p>", unsafe_allow_html=True)

    archivo = st.file_uploader("📸 Subir imagen de muestra", type=['jpg', 'jpeg', 'png'])

    if archivo:
        img = Image.open(archivo).convert("RGB")
        st.image(img, use_container_width=True)
        
        if st.button("🚀 INICIAR DIAGNÓSTICO PROFESIONAL"):
            with st.spinner('⏳ Analizando...'):
                try:
                    prompt = "Actúa como experto agrónomo de La Clementina (lcagro.com.ar). Identifica el problema y da: Diagnóstico, Producto y Dosis."
                    response = model.generate_content([prompt, img])
                    st.markdown("### ✅ Dictamen Técnico:")
                    st.markdown(f'<div class="resultado-card">{response.text}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error("Error al procesar la imagen.")

    st.markdown("<br><br><center><small>© 2026 LA CLEMENTINA</small></center>", unsafe_allow_html=True)
