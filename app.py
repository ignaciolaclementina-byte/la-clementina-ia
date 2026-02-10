import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual Blindado
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-attachment: fixed;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label { color: white !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; border: none; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 Acceso Privado</h1>", unsafe_allow_html=True)
    if st.text_input("Contraseña:", type="password") == "clementina2024":
        if st.button("INGRESAR"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. Interfaz
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.camera_input("📸 Tomar foto")
if not archivo:
    archivo = st.file_uploader("📁 O subir archivo", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                # Verificación de Secrets
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("❌ ERROR: No cargaste la GOOGLE_API_KEY en los Secrets de Streamlit.")
                    st.stop()
                
                # Configuración de Google
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # Forzamos el uso de Gemini 1.5 Flash (el único que permite visión gratis estable)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prompt con tus productos reales
                prompt = (
                    "Sos un Ingeniero Agrónomo de La Clementina S.A. "
                    "Analizá la imagen fitosanitaria. "
                    "RECOMENDACIÓN: Usá SOLO estos productos de nuestro stock: "
                    "Solomon, Starkle, Ampligo-Zariva, Lambda, Boomer, Eminent, Belt, Idaten. "
                    "Coadyuvantes: Optimizer, Rizo Spray Extremo, Integrum, Fulltec, Zen."
                )
                
                # Llamada a la IA
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA no pudo interpretar la imagen. Probá con otra.")

            except Exception as e:
                st.error(f"❌ ERROR DE SISTEMA: {str(e)}")
                st.info("Si el error dice '403' o 'API_KEY_INVALID', tu clave de Google no funciona.")
