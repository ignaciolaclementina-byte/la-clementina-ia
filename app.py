import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. CONFIGURACIÓN
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

VADEMECUM_CLEMENTINA = "ADHERENTES, BIOESTIMULANTES, FUNGICIDAS, HERBICIDAS, INSECTICIDAS."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. TRADUCCIÓN FORZADA (CSS)
st.markdown("""
    <style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop"); background-size: cover; }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; }
    
    /* TRADUCCIÓN DE BOTONES */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"]:before { content: "Arrastrá tu foto acá o"; color: white; font-weight: bold; }
    
    div[data-testid="stCameraInput"] button { font-size: 0px !important; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box { background-color: white !important; padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32; }
    .reporte-box * { color: black !important; }
    .stButton>button { width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold; }
    .btn-whatsapp { display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; text-decoration: none; font-weight: bold; text-align: center; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí una imagen", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                img = Image.open(foto).convert('RGB')
                response = model.generate_content(["Diagnóstico agronómico en español para San Jorge.", img])
                st.session_state['reporte'] = response.text
                st.markdown(f"<div class='reporte-box'><b>📋 INFORME:</b><br><br>{response.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error de Cuota: Google está saturado, esperá 1 minuto y probá de nuevo.")

# 4. WHATSAPP Y FIRMA
if 'reporte' in st.session_state:
    link = f"https://wa.me/?text={urllib.parse.quote(st.session_state['reporte'])}"
    st.markdown(f"<a href='{link}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; border-top: 1px solid white; padding: 20px;'><p style='color: white;'>Creado por</p><p style='color: #4CAF50; font-size: 20px; font-weight: bold;'>IGNACIO DIAZ</p></div>", unsafe_allow_html=True)
