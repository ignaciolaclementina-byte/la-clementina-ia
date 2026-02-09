import streamlit as st
import google.generativeai as genai
from PIL import Image

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

# --- CONFIGURACIÓN IA (INTELIGENTE) ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    # Buscamos qué modelo está disponible para no errarle al nombre
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    # Elegimos el mejor disponible (priorizando flash)
    modelo_nombre = next((m for m in modelos if 'flash' in m), modelos[0])
    model = genai.GenerativeModel(modelo_nombre)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
st.write(f"Conectado al motor: **{modelo_nombre.split('/')[-1]}**")

archivo = st.file_uploader("📸 Subí la foto aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('⌛ Analizando cultivo...'):
            try:
                prompt = "Sos un ingeniero agrónomo experto. Identifica el cultivo, el problema y da un tratamiento con productos y dosis."
                response = model.generate_content([prompt, img])
                st.success("### ✅ Dictamen:")
                st.write(response.text)
            except Exception as e:
                st.error("❌ Falló el análisis.")
                st.info(f"Detalle técnico: {str(e)}")
