import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (PARA DUPLICAR CAPACIDAD)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", 
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

# VADEMÉCUM PROPIO
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO CON FONDO DE SOJA (CSS)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.4)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center;
    }
    .titulo { color: white; text-align: center; font-size: 34px; font-weight: bold; text-shadow: 3px 3px 6px black; }
    .sub-titulo { color: #f0f0f0; text-align: center; font-size: 18px; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }

    /* TRADUCCIONES */
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32;
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold;
        height: 50px; font-size: 18px; border: none;
    }
    .btn-whatsapp {
        display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; text-align: center; width: 100%;
    }
    .stExpander { background-color: rgba(0,0,0,0.7) !important; border-radius: 15px; }
    .stExpander p { color: white !important; }
    div[data-testid="stWidgetLabel"] p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-titulo'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# 4. AYUDA CÁMARA
with st.expander("❓ ¿PROBLEMAS CON LA CÁMARA? TOCÁ ACÁ"):
    st.write("1. Permiso: Tocá el candado 🔒 al lado del link y activá 'Cámara'.")
    st.write("2. WhatsApp: Tocá los 3 puntitos (⋮) arriba y elegí 'Abrir en el navegador'.")
    st.write("3. Plan B: Sacá la foto normal y usá '📁 GALERÍA'.")

# 5. CARGA DE IMAGEN
opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    # AQUÍ ESTABA EL ERROR (image_a723f1.png): Ahora está cerrado correctamente
    foto = st.file_uploader("Subí una imagen para analizar", type=["jpg", "png", "jpeg"])

if foto:
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            listo = False
