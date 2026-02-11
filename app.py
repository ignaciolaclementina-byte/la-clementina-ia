import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", 
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

VADEMECUM = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO "SOJA PREMIUM" (CSS)
st.markdown("""
    <style>
    /* Fondo de soja con desenfoque suave */
    .stApp {
        background: url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Contenedor central traslúcido */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
    }

    /* Tarjeta blanca para el contenido */
    .main-card {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }

    .titulo { color: #1B5E20; text-align: center; font-size: 36px; font-weight: bold; margin-bottom: 5px; }
    .sub { color: #388E3C; text-align: center; font-size: 18px; margin-bottom: 30px; font-weight: bold; }
    
    /* Estilo de botones y controles */
    .stButton>button {
        width: 100%; border-radius: 15px; background-color: #2E7D32 !important;
        color: white !important; height: 55px; font-size: 18px; border: none; font-weight: bold;
    }
    .btn-wa {
        display: block; background-color: #25D366; color: white !important; padding: 15px;
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; font-size: 18px;
    }
    
    /* Caja de reporte */
    .reporte-box {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        color: #1a1a1a !important; border-left: 12px solid #2E7D32;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 20px;
    }
    
    /* Etiquetas en negro para que se lean bien */
    label, p, span { color: #1a1a1a !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONTENIDO PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# Contenedor de entrada
with st.container():
    opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)
    
    if opcion == "📸 CÁMARA":
        foto = st.camera_input("")
    else:
        foto = st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando cultivo...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como Agrónomo experto de San Jorge. Da diagnóstico y receta usando: {VADEMECUM}. Sé técnico pero claro. Respuesta en español."
                    res = model.generate_content([prompt, img])
                    
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except:
                    continue
            if not exito:
                st.error("⚠️ Sistema saturado. Reintentá en un minuto.")

# 4. BOTÓN WHATSAPP
if 'rep' in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    link = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; color: white !important;'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
