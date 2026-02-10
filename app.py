import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# --- ESTILOS (FONDO SOJA) ---
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

# --- LOGIN ---
if "logueado" not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.title("🔐 Acceso La Clementina")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("INGRESAR"):
        if clave == "clementina2024":
            st.session_state.logueado = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- INTERFAZ ---
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico con Stock Real 2026")

opcion = st.radio("Origen de la imagen:", ["📸 Cámara", "📁 Galería"], horizontal=True)
archivo = st.camera_input("Capturar") if opcion == "📸 Cámara" else st.file_uploader("Subir", type=["jpg", "png"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=350, caption="Muestra seleccionada")
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Consultando con el Ingeniero IA..."):
            try:
                # 1. Verificación de Clave
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("⚠️ ERROR: No configuraste la clave en 'Secrets' de Streamlit.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 2. Instrucciones basadas en tu Excel
                instruccion = """
                Sos ingeniero agrónomo de La Clementina. 
                Analiza la imagen y recomienda SOLO estos productos de nuestro stock:
                INSECTICIDAS: Solomon, Bifentrin 25%, Starkle, Ampligo-Zariva, Lambda Microencapsulada, Boomer, Eminent, Belt 480 SC, Idaten.
                ADHERENTES: Optimizer, Rizo Spray Extremo, Integrum, Fulltecmax, Alquimia, Rizospray Zen, Tropgreen.
                Responde: Diagnóstico, Producto del Stock y Dosis.
                """
                
                # 3. Intento de Generación
                response = model.generate_content([instruccion, img])
                
                if response:
                    st.success("✅ DICTAMEN GENERADO:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA no devolvió texto. Intente con una foto más nítida.")

            except Exception as e:
                # Esto nos dirá el error real (API_KEY_INVALID, etc.)
                st.error(f"❌ ERROR TÉCNICO: {str(e)}")
                st.info("Si el error dice 'API_KEY_INVALID', revisá la clave en Streamlit Cloud.")
