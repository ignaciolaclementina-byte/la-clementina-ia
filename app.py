import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilos (Fondo de Soja Garantizado)
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
h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; }
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
st.write("### Diagnóstico con Stock 2026")

archivo = st.camera_input("Sacar foto al cultivo")
if not archivo:
    archivo = st.file_uploader("O subir desde galería", type=["jpg", "png", "jpeg"])

if archivo:
    # Mostramos la imagen
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 ANALIZAR AHORA"):
        if "GOOGLE_API_KEY" not in st.secrets:
            st.error("Falta la API KEY en los Secrets de Streamlit.")
        else:
            with st.spinner("Analizando..."):
                try:
                    # Configuración de IA
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Prompt con tus productos del Excel
                    productos_stock = "Solomon, Bifentrin, Starkle, Ampligo-Zariva, Lambda, Boomer, Eminent, Belt, Idaten. Coadyuvantes: Optimizer, Rizo Spray, Integrum, Zen."
                    prompt = f"Sos ingeniero agronomo de La Clementina. Analiza la imagen, identifica el problema y recomienda tratamiento usando SOLO estos productos: {productos_stock}. Se breve."
                    
                    # Enviar a la IA
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.success("✅ RECOMENDACIÓN TÉCNICA:")
                        st.write(response.text)
                    else:
                        st.error("La IA no pudo procesar la imagen. Intentá de nuevo.")
                except Exception as e:
                    st.error(f"Error técnico: {str(e)}")
