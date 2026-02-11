import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES (Seguridad Doble)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO CAMPERO (CSS)
st.markdown("""
    <style>
    /* Imagen de soja real de fondo */
    .stApp {
        background: url("https://images.pexels.com/photos/235925/pexels-photo-235925.jpeg?auto=compress&cs=tinysrgb&w=1920") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Filtro para que el texto se lea impecable */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.4) !important;
    }

    /* Títulos en Verde Agrónomo */
    .titulo { color: #1B5E20; text-align: center; font-size: 36px; font-weight: bold; text-shadow: 2px 2px 4px white; margin-top: -50px; }
    .sub { color: #2E7D32; text-align: center; font-size: 19px; font-weight: bold; margin-bottom: 25px; text-shadow: 1px 1px 2px white; }
    
    /* Etiquetas en NEGRO fuerte */
    label, p, span, .stMarkdown { color: black !important; font-weight: bold !important; }

    /* Botones de alta visibilidad */
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #1B5E20 !important; 
        color: white !important; height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white;
    }
    
    /* Caja de resultados blanca */
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    .reporte-box * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Corrección de sintaxis línea 82
    foto = st.file_uploader("Elegí una imagen para analizar", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR RECETA TÉCNICA'):
        with st.spinner('Procesando...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Ingeniero Agrónomo de San Jorge. Da diagnóstico y receta según: {VADEMECUM}. Respuesta en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except: continue
            if not exito: st.error("Límite de Google alcanzado. Reintentá.")

if 'rep' in st.
