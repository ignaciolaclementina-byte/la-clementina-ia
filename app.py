import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label, span { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; border: none; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "entrar" not in st.session_state:
    st.session_state.entrar = False

if not st.session_state.entrar:
    st.title("🔐 Acceso Privado")
    passw = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR"):
        if passw == "clementina2024":
            st.session_state.entrar = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# 4. Interfaz Principal
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico y Stock 2026")

# Entrada de imagen simplificada
foto = st.camera_input("📸 Tomar foto")
archivo = st.file_uploader("📁 O subir desde galería", type=["jpg", "png", "jpeg"])

img_final = foto if foto else archivo

if img_final:
    img_ready = Image.open(img_final)
    st.image(img_ready, width=400)
    
    if st.button("🚀 ANALIZAR MUESTRA"):
        with st.spinner("Procesando diagnóstico..."):
            try:
                # Verificación de API Key
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("Error: Falta GOOGLE_API_KEY en Secrets.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Instrucción basada en tu Excel
                productos = "INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo-Zariva, Lambda, Boomer, Eminent, Belt, Idaten. ADHERENTES: Optimizer, Rizo Spray, Integrum, Fulltec, Alquimia, Zen."
                prompt = f"Sos ingeniero agrónomo de La Clementina. Identificá el problema en la foto. Recomendá tratamiento SOLO con estos productos de nuestro stock: {productos}. Sé breve y profesional."
                
                # Respuesta de la IA
                response = model.generate_content([prompt, img_ready])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
                else:
                    st.warning("No se pudo generar texto. Intentá con otra foto.")
            
            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
                st.info("Tip: Revisá que la API Key sea válida y realizá un 'Reboot' en Streamlit Cloud.")
