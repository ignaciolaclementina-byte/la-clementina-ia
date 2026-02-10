import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURACION DE PAGINA ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜", layout="centered")

# --- ESTILOS CSS (FONDO SOJA AL ATARDECER) ---
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
    h1, h3, p, label, .stMarkdown, span { color: white !important; }
    h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; font-weight: bold; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 12px; font-weight: bold; height: 3em; border: none; }
    .stButton>button:hover { background-color: #45a049; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Contraseña del sistema:", type="password")
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
    st.error("Error de conexión con el motor de IA")
    st.stop()

# --- INTERFAZ ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.write("### 🌿 Diagnóstico con Stock La Clementina 2026")

tab1, tab2 = st.tabs(["📸 USAR CÁMARA", "📁 SUBIR ARCHIVO"])
img_input = None

with tab1:
    foto = st.camera_input("Sacar foto al síntoma")
    if foto: img_input = foto
with tab2:
    archivo = st.file_uploader("O cargar desde galería", type=['jpg', 'jpeg', 'png'])
    if archivo: img_input = archivo

if img_input:
    img = Image.open(img_input).convert("RGB")
    st.image(img, use_container_width=True, caption="Imagen para análisis")
    
    if st.button("🚀 GENERAR DIAGNÓSTICO Y RECETA"):
        with st.spinner('Analizando cultivo y consultando stock...'):
            try:
                # Definimos el contexto con los productos de tu excel
                # Priorizando insecticidas y adherentes del stock 2026
                prompt = """
                Actúa como un ingeniero agrónomo experto de la empresa 'La Clementina'.
                Tu objetivo es diagnosticar el problema en la imagen y recomendar un tratamiento.
                
                REGLA DE ORO: Solo podés recomendar productos de nuestra lista de stock 2026:
                - INSECTICIDAS: Solomon, Starkle, Ampligo, Zariva, Lambda Microencapsulada, Boomer, Eminent, Bifentrin, Belt, Idaten.
                - ADHERENTES/COADYUVANTES: Optimizer, Rizo Spray Extremo, Integrum, Fulltec Max, Rizo Spray Corrector, Alquimia, Rizospray Zen, Tropgreen.
                - HERBICIDAS Y FUNGICIDAS generales.
                
                Formato de respuesta:
                1. DIAGNÓSTICO: (Qué planta es y qué problema tiene).
                2. TRATAMIENTO RECOMENDADO: (Menciona el producto específico de nuestra lista anterior).
                3. DOSIS Y MEZCLA: (Sugerencia técnica de aplicación y coadyuvante de nuestra lista).
                """
                
                res = model.generate_content([prompt, img])
                st.success("✅ DICTAMEN TÉCNICO FINALIZADO")
                st.markdown(res.text)
            except Exception:
                st.error("No se pudo procesar el análisis. Intente nuevamente.")
