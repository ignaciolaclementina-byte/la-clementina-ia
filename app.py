import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración básica
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso La Clementina")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Entrar"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- CONFIGURACIÓN IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    # Cambiamos el nombre del modelo a la versión más compatible
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
except Exception as e:
    st.error(f"Error técnico: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
st.write("Cargá una foto para el diagnóstico experto.")

archivo = st.file_uploader("📸 Subí la foto aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('⌛ Analizando con IA...'):
            try:
                prompt = "Sos un ingeniero agrónomo experto. Identifica el cultivo, el problema y da un tratamiento con productos y dosis."
                response = model.generate_content([prompt, img])
                st.success("### ✅ Dictamen:")
                st.write(response.text)
            except Exception as e:
                st.error("❌ El sistema no pudo procesar la imagen.")
                st.info(f"Detalle técnico: {str(e)}")
