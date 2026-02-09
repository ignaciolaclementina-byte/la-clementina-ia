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
    # Intentamos leer la llave de los Secrets
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error en la configuración técnica: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
archivo = st.file_uploader("📸 Subí la foto aquí:", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner('Analizando...'):
            try:
                # El pedido a la IA
                prompt = "Sos un ingeniero agrónomo. Analizá esta imagen de cultivo. Identificá el problema y recomendá tratamiento con productos y dosis."
                response = model.generate_content([prompt, img])
                
                st.success("### ✅ Dictamen:")
                st.write(response.text)
            except Exception as e:
                # ESTO ES LO IMPORTANTE: Ahora nos va a decir el error real
                st.error("❌ ERROR TÉCNICO DETECTADO:")
                st.info(f"Detalle del error: {str(e)}")
                st.warning("Si el error dice 'API_KEY_INVALID', hay que generar una llave nueva en Google AI Studio.")
