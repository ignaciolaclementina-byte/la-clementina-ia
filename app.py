import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVES Y CONFIGURACIÓN
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. EL SKIN DEFINITIVO (Usamos una imagen de respaldo por si falla el link)
st.markdown("""
    <style>
    /* Aplicamos el fondo directamente al contenedor principal */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.4)), 
                    url("https://www.agrofy.com.ar/media/catalog/product/cache/1/image/850x/040ec09b1e35df139433887a97daa66f/s/o/soja_1.jpg") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Quitamos el blanco sólido que te molestaba */
    .stApp { background: transparent !important; }
    
    /* Títulos en Verde para que se vean bien sobre el campo */
    .titulo { color: #1B5E20; text-align: center; font-size: 36px; font-weight: bold; text-shadow: 2px 2px 5px white; }
    .sub { color: #2E7D32; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; text-shadow: 1px 1px 3px white; }
    
    /* Texto de controles en NEGRO para que lo leas perfecto */
    label, p, span, .stMarkdown { color: black !important; font-weight: bold !important; }

    /* Botón PRO */
    .stButton>button { 
        width: 100%; border-radius: 15px; background-color: #2E7D32 !important; 
        color: white !important; height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white;
    }
    
    /* Caja de resultados blanca pura para contraste */
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 20px; 
        color: black !important; border-left: 10px solid #2E7D32; box-shadow: 0px 5px 15px rgba(0,0,0,0.3);
    }
    .reporte-box * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Corrección de comillas y cierre de paréntesis para evitar errores
    foto = st.file_uploader("Subí una imagen de tu lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR INFORME TÉCNICO'):
        with st.spinner('Analizando cultivo...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como Agrónomo experto de San Jorge. Da un diagnóstico y receta comercial usando este vademécum: {VADEMECUM}. Respuesta técnica en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except: continue
            if not exito: st.error("Sistema saturado. Esperá un minuto.")

if 'rep' in st.session_state:
    link = urllib.parse.quote(f"🚜 *CONSULTA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)
