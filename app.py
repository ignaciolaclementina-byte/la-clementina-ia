import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# 2. Estilo Visual (Fondo Soja Atardecer)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    border: 2px solid #4CAF50;
    padding: 2rem;
    border-radius: 15px;
}
h1, h3, p, label, .stMarkdown { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; font-weight: bold; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; border: none; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso La Clementina")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("INGRESAR"):
        if clave == "clementina2024":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# 4. Interfaz Principal
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico con Stock Real 2026")

# Selector de entrada simple
archivo = st.camera_input("📸 Sacar foto al cultivo")
if not archivo:
    archivo = st.file_uploader("📁 O subir desde galería", type=["jpg", "png", "jpeg"])

if archivo:
    # Procesamiento de imagen para que no sea pesada
    img = Image.open(archivo)
    st.image(img, width=400, caption="Imagen cargada")
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        if "GOOGLE_API_KEY" not in st.secrets:
            st.error("Falta configurar la GOOGLE_API_KEY en Secrets.")
        else:
            with st.spinner("Analizando muestra..."):
                try:
                    # Configuración IA
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Productos de tu lista
                    productos = "Insecticidas: Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. Adherentes: Optimizer, Rizo Spray, Integrum, Fulltec, Zen."
                    
                    prompt = f"Sos ingeniero agrónomo de La Clementina S.A. Identificá el cultivo y la plaga/enfermedad en la foto. Recomendá tratamiento con estos productos: {productos}."
                    
                    # Enviar a la IA (con manejo de errores de seguridad)
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.success("✅ RECOMENDACIÓN TÉCNICA:")
                        st.markdown(response.text)
                    else:
                        st.warning("La IA no pudo generar una respuesta. Probá con otra foto más clara.")
                
                except Exception as e:
                    st.error(f"Error técnico: {str(e)}")
                    st.info("Revisá que la clave API sea válida y tenga facturación activa o cuota disponible.")
