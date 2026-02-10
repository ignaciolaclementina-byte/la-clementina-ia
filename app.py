import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label, .stMarkdown { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "log" not in st.session_state: st.session_state.log = False
if not st.session_state.log:
    st.title("🔐 Acceso La Clementina")
    if st.text_input("Clave:", type="password") == "clementina2024":
        if st.button("ENTRAR"):
            st.session_state.log = True
            st.rerun()
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico y Stock 2026")

archivo = st.camera_input("📸 Cámara")
if not archivo:
    archivo = st.file_uploader("📁 Galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=300)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            try:
                # 1. Configurar API
                api_key = st.secrets["GOOGLE_API_KEY"]
                genai.configure(api_key=api_key)
                
                # 2. Configurar Modelo
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 3. Prompt basado en tu lista (Solomon, Ampligo, etc.)
                productos = "Insecticidas: Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. Adherentes: Optimizer, Rizo Spray, Integrum, Fulltec, Alquimia, Zen."
                prompt = f"Sos ingeniero agrónomo de La Clementina. Analizá la foto y diagnosticá. Recomendá productos de este stock: {productos}."
                
                # 4. Generar
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
                else:
                    st.error("La IA no devolvió respuesta. Probá con otra foto.")
                    
            except Exception as e:
                st.error(f"❌ ERROR CRÍTICO: {str(e)}")
                st.info("Si el error menciona '429' o 'Quota', es que llegamos al límite gratuito de la clave.")
