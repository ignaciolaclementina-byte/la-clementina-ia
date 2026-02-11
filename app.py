import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (PARA DUPLICAR LA CUOTA)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", 
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

# VADEMÉCUM
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO CON FONDO DE SOJA Y TRADUCCIONES
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center;
    }
    .titulo { color: white; text-align: center; font-size: 34px; font-weight: bold; text-shadow: 3px 3px 6px rgba(0,0,0,0.8); }
    .sub-titulo { color: #f0f0f0; text-align: center; font-size: 18px; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }

    /* TRADUCCIÓN BOTONES */
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold;
        height: 50px; font-size: 18px; border: none; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .btn-whatsapp {
        display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; text-align: center; width: 100%; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    /* AYUDA EXPANDER */
    .stExpander { background-color: rgba(0,0,0,0.6) !important; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); }
    .stExpander p, .stExpander label { color: white !important; }
    
    /* RADIO BUTTONS TEXTO */
    div[data-testid="stWidgetLabel"] p { color: white !important; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-titulo'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# 4. MANUAL DE AYUDA (Colapsado)
with st.expander("❓ ¿PROBLEMAS CON LA CÁMARA? TOCÁ ACÁ"):
    st.write("""
    1. **Permiso denegado:** Tocá el candado 🔒 al lado del link y activá 'Cámara'.
    2. **Desde WhatsApp:** Tocá los 3 puntitos (⋮) arriba y elegí 'Abrir en el navegador'.
    3. **Plan B:** Sacá la foto con tu cámara normal y usá '📁 GALERÍA'.
    """)

# 5. SELECCIÓN DE ORIGEN
opcion = st.radio("SELECCIONÁ ORIGEN DE LA IMAGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    foto = st.file_uploader("Subí una imagen para analizar", type=["jpg
