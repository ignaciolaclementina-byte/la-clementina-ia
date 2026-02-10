import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

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
    h1, h3, p, label, .stMarkdown, span { color: white !important; }
    h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; font-weight: bold; }
    .stButton>button { width: 100%; background-color: #2e7d32; color: white; border-radius: 12px; font-weight: bold; height: 3em; border: none; }
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
    foto = st.camera_input("Sacar foto")
    if foto: img_input = foto
with tab2:
    archivo = st.file_uploader("Subir imagen", type=['jpg', 'jpeg', 'png'])
    if archivo: img_input = archivo

if img_input:
    img = Image.open(img_input).convert("RGB")
    st.image(img, use_container_width=True)
    
    if st.button("🚀 GENERAR DIAGNÓSTICO"):
        with st.spinner('Analizando...'):
            try:
                # Definimos el texto de instrucción de forma segura
                instruccion = (
                    "Actúa como ingeniero agrónomo de La Clementina. "
                    "Analiza la imagen, identifica cultivo y problema. "
                    "Recomienda SOLO productos de nuestro stock: "
                    "Insecticidas (Solomon, Ampligo, Belt, Starkle, Idaten, Boomer, Eminent), "
                    "Adherentes (Optimizer, Rizo Spray Extremo, Rizospray Zen, Alquimia, Integrum). "
                    "Da diagnóstico, producto y dosis."
                )
                
                res = model.generate_content([instruccion, img])
                resultado_texto = res.text
                
                st.success("✅ DICTAMEN FINALIZADO")
                st.markdown(resultado_texto)
                
                # --- BOTÓN DE WHATSAPP ---
                texto_ws = urllib.parse.quote(f"Hola! Te envío el diagnóstico de La Clementina IA:\n\n{resultado_texto}")
                link_ws = f"https://wa.me/?text={texto_ws}"
                st.markdown(f'<a href="{link_ws}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border-radius:12px; font-weight:bold; height:3em; border:none; cursor:pointer;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error("Error técnico al procesar. Intente de nuevo.")
