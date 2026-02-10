import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- INTERFAZ MODERNA ---
st.set_page_config(page_title="La Clementina IA", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9f5; }
    .main-title { color: #1b5e20; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 0px; }
    .sub-title { text-align: center; color: #555; margin-bottom: 30px; }
    .diagnostico-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #2e7d32;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #1a1a1a;
        font-size: 18px;
        line-height: 1.6;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        font-size: 20px;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-title'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Diagnóstico de Precisión para el Campo</div>", unsafe_allow_html=True)

# --- MENÚ LATERAL ---
with st.sidebar:
    st.header("⚙️ OPCIONES")
    modo = st.radio("¿Qué vas a usar?", ["📸 Cámara en vivo", "📁 Galería de fotos"])
    st.divider()
    st.write("📌 **Consejo:** Asegurate de que haya buena luz sobre la hoja para un mejor resultado.")

# --- CUERPO PRINCIPAL ---
col_foto, col_info = st.columns([1, 1], gap="large")

with col_foto:
    if modo == "📸 Cámara en vivo":
        foto = st.camera_input("Capturá el problema")
    else:
        foto = st.file_uploader("Subí tu imagen técnica", type=["jpg", "png", "jpeg"])

with col_info:
    if foto:
        st.image(foto, caption="Imagen a analizar", use_container_width=True)
        if st.button('🚀 GENERAR DICTAMEN TÉCNICO'):
            with st.spinner('Analizando síntomas...'):
                try:
                    # Lógica de IA (Buscador automático de modelo)
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(modelos[0])
                    
                    img = Image.open(foto).convert('RGB')
                    img.thumbnail((500, 500))
                    
                    prompt = "Sos Ingeniero Agrónomo. Analizá la imagen y respondé con este formato: 1. DIAGNÓSTICO, 2. CAUSAS, 3. TRATAMIENTO RECOMENDADO. Sé breve."
                    response = model.generate_content([prompt, img])
                    
                    # Mostrar resultado sin errores de formato
                    texto_final = response.text
                    st.markdown("### 📋 Informe del Especialista:")
                    st.markdown(f"<div class='diagnostico-card'>{texto_final}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
    else:
        st.info("👋 Bienvenida/o. Por favor, cargá una foto o activá la cámara para empezar.")

st.divider()
st.caption("La Clementina IA - Desarrollado para optimizar el rendimiento de tus cultivos.")
