import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- DISEÑO DE INTERFAZ (CSS) ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f1;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: #e8f5e9;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #1b5e20;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .diagnostico-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #2e7d32;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_stdio=True)

# --- CABECERA ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Asistente Inteligente para Diagnóstico de Cultivos</p>", unsafe_allow_html=True)
st.divider()

# --- LÓGICA DE ANÁLISIS ---
def obtener_diagnostico(foto):
    img = Image.open(foto).convert('RGB')
    img.thumbnail((600, 600))
    
    # Buscador de modelos para evitar errores 404
    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model = genai.GenerativeModel(modelos[0])
    
    prompt = """Sos un Ingeniero Agrónomo experto. 
    Analizá la imagen y respondé con este formato:
    1. DIAGNÓSTICO: Qué problema tiene.
    2. CAUSA: Por qué ocurrió.
    3. TRATAMIENTO: Qué producto o acción aplicar.
    Sé directo y profesional."""
    
    response = model.generate_content([prompt, img])
    return response.text

# --- ENTRADA DE DATOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Captura")
    archivo_cam = st.camera_input("Sacar foto ahora")

with col2:
    st.subheader("📂 Galería")
    archivo_gal = st.file_uploader("Cargar imagen", type=["jpg", "png", "jpeg"])

# Usar el archivo que esté disponible
archivo = archivo_cam if archivo_cam else archivo_gal

# --- RESULTADOS ---
if archivo:
    st.image(archivo, caption="Muestra cargada", use_container_width=True)
    
    if st.button('🚀 INICIAR ANÁLISIS TÉCNICO'):
        with st.spinner('Procesando datos del lote...'):
            try:
                res = obtener_diagnostico(archivo)
                st.markdown("### ✅ Resultados del Análisis")
                st.markdown(f"<div class='diagnostico-box'>{res}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error en la conexión: {e}")

st.divider()
st.caption("La Clementina IA - Potenciado por Gemini 1.5 Flash")
