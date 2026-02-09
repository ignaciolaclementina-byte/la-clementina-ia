import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración básica
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# --- ACCESO CON CONTRASEÑA ---
if "acceso_ok" not in st.session_state:
    st.session_state["acceso_ok"] = False

if not st.session_state["acceso_ok"]:
    st.title("🔐 Acceso Restringido")
    password = st.text_input("Ingresá la contraseña:", type="password")
    if st.button("Entrar"):
        if password == "clementina2024":
            st.session_state["acceso_ok"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# --- CONFIGURACIÓN DE IA ---
try:
    # Lee la llave desde los Secrets de Streamlit
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Falta la configuración de GOOGLE_API_KEY en Streamlit.")
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
archivo = st.file_uploader("📸 Subí la foto de la planta", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('Analizando...'):
            try:
                res = model.generate_content(["Identifica el cultivo y diagnóstico de plagas con tratamiento.", img])
                st.success("### Análisis:")
                st.write(res.text)
            except:
                st.error("Error al procesar. Probá con otra foto.")
