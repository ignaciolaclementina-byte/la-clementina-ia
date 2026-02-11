import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. DATOS DE ACCESO
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO AGRO-REALISTA (Soja de Verdad)
st.markdown("""
    <style>
    .stApp {
        /* Imagen de cultivo de soja real y profesional */
        background: url("https://images.unsplash.com/photo-1594904351111-a072f80b1a71?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Filtro para que el texto resalte sobre las plantas */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.35) !important;
    }

    .titulo { color: #1B5E20; text-align: center; font-size: 38px; font-weight: bold; text-shadow: 2px 2px 4px white; margin-top: -30px; }
    .sub { color: #2E7D32; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; text-shadow: 1px 1px 2px white; }
    
    /* Etiquetas en NEGRO fuerte para el sol del mediodía */
    label, p, span, .stMarkdown { color: black !important; font-weight: bold !important; font-size: 17px !important; }

    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #1B5E20 !important; 
        color: white !important; height: 55px; font-size: 20px; border: 2px solid white; font-weight: bold;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px;
    }
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CUERPO DE LA APP
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Elegí una imagen para analizar", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR RECETA TÉCNICA'):
        with st.spinner('Procesando datos del lote...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Ingeniero Agrónomo de San Jorge. Da diagnóstico y receta según: {VADEMECUM}. Respuesta técnica en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME DE CAMPO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except: continue

if 'rep' in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    msg = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={msg}' target='_blank' class='btn-wa'>📲 ENVIAR A MI WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; color: #1B5E20;'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
