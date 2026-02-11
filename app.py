import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES (CON RESPALDO)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]

VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. SKIN: FORZANDO EL LOTE DE SOJA (CSS)
st.markdown("""
    <style>
    /* El truco para que el fondo no sea negro */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* Texto en blanco con sombra para que se lea sobre el verde */
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: bold; text-shadow: 2px 2px 5px black; }
    .sub { color: white; text-align: center; font-size: 18px; text-shadow: 1px 1px 3px black; margin-bottom: 20px; }
    p, label, span { color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px black; }

    /* Caja del diagnóstico: Blanca para que resalte */
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #2E7D32;
    }
    .reporte-box * { color: black !important; text-shadow: none !important; }

    /* Botones Pro */
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2E7D32 !important; color: white !important; height: 50px; border: 2px solid white; }
    .btn-wa { display: block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 25px; text-decoration: none; text-align: center; border: 2px solid white; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

with st.expander("❓ AYUDA CON LA CÁMARA"):
    st.write("1. Tocá el candado 🔒 arriba y activá la cámara.")
    st.write("2. Si estás en WhatsApp, tocá los 3 puntitos y elegí 'Abrir en navegador'.")

opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí tu foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como Agrónomo de San Jorge. Diagnóstico y receta usando: {VADEMECUM}. En español."
                    res = model.generate_content([prompt, img])
                    
                    st.session_state['rep'] = res.text
                    html = res.text.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO:</b><br><br>{html}</div>", unsafe_allow_html=True)
                    break
                except:
                    continue

if 'rep' in st.session_state:
    link = urllib.parse.quote(f"🚜 *CONSULTA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
