import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVES Y VADEMECUM
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. EL SKIN DE CAMPO REAL
st.markdown("""
    <style>
    /* Ponemos la imagen del campo de fondo */
    .stApp {
        background: url("https://images.unsplash.com/photo-1594904351111-a072f80b1a71?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Capa para que el fondo no tape el texto */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.3) !important;
    }

    /* Títulos en un verde monte fuerte */
    .titulo { color: #1B5E20; text-align: center; font-size: 38px; font-weight: bold; text-shadow: 2px 2px 4px white; }
    .sub { color: #2E7D32; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 30px; text-shadow: 1px 1px 2px white; }
    
    /* Controles y etiquetas en NEGRO para que los veas claritos */
    label, p, span, .stMarkdown { color: black !important; font-weight: bold !important; }

    /* Botones y Cajas */
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #1B5E20 !important; 
        color: white !important; height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white;
    }
    
    /* Caja de resultados blanca y prolija */
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    .reporte-box * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí tu imagen", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR AHORA'):
        with st.spinner('Escaneando cultivo...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Ingeniero Agrónomo San Jorge. Diagnóstico y receta: {VADEMECUM}. Respuesta técnica en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except: continue
            if not exito: st.error("Límite de Google. Intentá de nuevo.")

if 'rep' in st.session_state:
    link = urllib.parse.quote(f"🚜 *CONSULTA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)
