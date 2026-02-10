import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual (Fondo Soja Atardecer)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-attachment: fixed;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.9);
    padding: 20px;
    border-radius: 15px;
    border: 2px solid #4CAF50;
    margin-top: 20px;
}
h1, h3, p, label { color: white !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; font-weight: bold; height: 50px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Login Simple
if "acceso" not in st.session_state:
    st.session_state.acceso = False

if not st.session_state.acceso:
    st.markdown("<h1>🔐 Acceso Privado</h1>", unsafe_allow_html=True)
    clave = st.text_input("Ingresar Contraseña:", type="password")
    if st.button("ENTRAR"):
        if clave == "clementina2024":
            st.session_state.acceso = True
            st.rerun()
        else:
            st.error("Clave Incorrecta")
    st.stop()

# 4. Interfaz Principal
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<h3>Diagnóstico y Stock 2026</h3>", unsafe_allow_html=True)

# Entrada única de imagen (Cámara o Galería según dispositivo)
archivo = st.file_uploader("📸 Subir o Tomar Foto del Cultivo", type=["jpg", "jpeg", "png"])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Analizando muestra..."):
            try:
                # Configuración de API
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("No se encontró la GOOGLE_API_KEY en los Secrets de Streamlit.")
                else:
                    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # Productos cargados de tu Excel
                    productos = "INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo-Zariva, Lambda, Boomer, Eminent, Belt, Idaten. ADHERENTES: Optimizer, Rizo Spray Extremo, Integrum, Fulltec, Zen."
                    
                    # Pedido a la IA
                    prompt = f"Sos ingeniero agrónomo de La Clementina. Analiza la imagen. Diagnostica cultivo y problema. Recomienda solo productos de este stock: {productos}. Da la dosis."
                    
                    response = model.generate_content([prompt, img])
                    
                    if response.text:
                        st.success("✅ INFORME TÉCNICO:")
                        st.markdown(response.text)
                    else:
                        st.error("La IA no pudo procesar la imagen.")
            except Exception as e:
                st.error(f"Error de sistema: {str(e)}")
