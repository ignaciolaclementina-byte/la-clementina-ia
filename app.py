import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API que ya sabemos que vuela
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

st.set_page_config(page_title="La Clementina IA", page_icon="🚜")

# --- ESTILO MEJORADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f0; }
    .reporte-final {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #2e7d32;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        color: #1a1a1a;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚜 LA CLEMENTINA IA")
st.write("Diagnóstico experto de cultivos al instante.")

# --- SELECCIÓN DE IMAGEN ---
with st.sidebar:
    st.header("Opciones")
    modo = st.radio("Fuente:", ["📸 Cámara", "📁 Galería"])

if modo == "📸 Cámara":
    foto = st.camera_input("Capturá la hoja")
else:
    foto = st.file_uploader("Subí tu foto", type=["jpg", "png", "jpeg"])

# --- PROCESAMIENTO ---
if foto:
    st.image(foto, caption="Imagen cargada", use_container_width=True)
    
    if st.button('🚀 GENERAR DICTAMEN TÉCNICO'):
        with st.spinner('Analizando planta...'):
            try:
                # Buscamos el modelo que esté vivo en tu servidor
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((600, 600))
                
                prompt = "Actuá como agrónomo experto. Analizá la imagen y da: 1- Diagnóstico, 2- Causa, 3- Tratamiento. Sé directo."
                response = model.generate_content([prompt, img])
                
                # ACÁ ESTÁ LA MAGIA: El reporte sale en una caja limpia
                st.markdown("### 📋 RESULTADO DEL ANÁLISIS:")
                st.markdown(f"<div class='reporte-final'>{response.text}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.info("Cargá una foto para ver el reporte aquí abajo.")
