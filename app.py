import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2232&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }
    .block-container {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 2.5rem;
        border-radius: 20px;
        border: 2px solid #4CAF50;
    }
    h1, h2, h3, p, li, label, .stMarkdown, span {
        color: white !important;
    }
    h1 {
        color: #4CAF50 !important;
        text-align: center;
        text-shadow: 2px 2px 4px #000000;
    }
    .stButton>button {
        width: 100%;
        background-color: #2e7d32;
        color: white;
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR"):
        if clave == "clementina2024":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- MOTOR IA ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("Error de conexión con la IA")
    st.stop()

# --- INTERFAZ ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.write("### 🌿 Diagnóstico con nuestra Lista de Productos")

tab1, tab2 = st.tabs(["📸 CÁMARA", "📁 GALERÍA"])
imagen_final = None

with tab1:
    foto = st.camera_input("Capturar síntoma en el lote")
    if foto: imagen_final = foto
with tab2:
    archivo = st.file_uploader("Subir foto", type=['jpg', 'jpeg', 'png'])
    if archivo: imagen_final = archivo

if imagen_final:
    img = Image.open(imagen_final).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR Y BUSCAR PRODUCTOS"):
        with st.spinner('Analizando y consultando disponibilidad...'):
            try:
                # Aquí inyectamos el conocimiento de tu lista de precios/productos
                prompt = """
                Sos el ingeniero agrónomo experto de LA CLEMENTINA. 
                Analizá la imagen y diagnosticá el problema.
                
                IMPORTANTE: Para el tratamiento, recomendá EXCLUSIVAMENTE productos que manejamos, como:
                - Insecticidas: Solomon, Ampligo, Belt, Starkle, Lambda, Boomer, Eminent, Idaten, etc.
                - Herbicidas y Fungicidas de nuestra lista de stock 2026.
                - Adherentes: Optimizer, Rizo Spray, Break Thru, etc.
                
                Estructura:
                1. Diagnóstico (Cultivo y problema).
                2. Recomendación de aplicación (Producto específico de nuestra lista y dosis).
                3. Sugerencia de adherente si es necesario.
                """
                res = model.generate_content([prompt, img])
                st.success("✅ INFORME TÉCNICO LA CLEMENTINA:")
                st.markdown(res.text)
            except Exception as e:
                st.error(f"Error en el análisis: {str(e)}")
