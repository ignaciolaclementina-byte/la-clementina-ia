import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVES Y VADEMECUM
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. SKIN "VERDE BLINDADO" (Sin imágenes externas para que no falle)
st.markdown("""
    <style>
    /* Fondo degradado dinámico (Verde Monte a Verde Campo) */
    .stApp {
        background: linear-gradient(135deg, #1B5E20 0%, #388E3C 50%, #4CAF50 100%) !important;
    }
    
    /* Eliminamos cualquier bloque blanco de Streamlit */
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background: transparent !important;
    }

    /* Tarjeta central con efecto cristal (Glassmorphism) */
    .main-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 25px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        margin-top: 20px;
    }

    /* Títulos con sombra blanca para que resalten sobre el verde */
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .sub { color: #e8f5e9; text-align: center; font-size: 18px; margin-bottom: 20px; font-weight: bold; }
    
    /* Etiquetas y texto en blanco */
    label, p, span { color: white !important; font-weight: bold !important; text-shadow: 1px 1px 2px black; }

    /* Botones Pro */
    .stButton>button {
        width: 100%; border-radius: 12px; background-color: white !important;
        color: #1B5E20 !important; height: 50px; font-size: 18px; border: none; font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .btn-wa {
        display: block; background-color: #25D366; color: white !important; padding: 15px;
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; 
        border: 2px solid white; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Caja de resultados: Blanca y sólida para lectura perfecta */
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 15px;
        color: #1a1a1a !important; border-left: 10px solid #2E7D32;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3); margin-top: 15px;
    }
    .reporte-box * { color: #1a1a1a !important; text-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# Ponemos los controles dentro de un contenedor para aplicar el estilo
with st.container():
    opcion = st.radio("ORIGEN DE IMAGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)
    
    if opcion == "📸 CÁMARA":
        foto = st.camera_input("")
    else:
        # Corregido error de comillas de capturas anteriores
        foto = st.file_uploader("Subí tu foto desde el celu", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True, caption="Imagen cargada")
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            listo = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Agrónomo San Jorge. Diagnóstico y receta: {VADEMECUM}. Respuesta técnica en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    listo = True
                    break
                except: continue
            if not listo: st.error("Límite de Google alcanzado. Reintentá en un minuto.")

if 'rep' in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    link = urllib.parse.quote(f"🚜 *CONSULTA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 MANDAR POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; color: white;'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
