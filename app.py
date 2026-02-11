import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. DATOS
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA")

# 2. DISEÑO AGRO (Fondo Verde Sólido + Imagen)
st.markdown("""
    <style>
    .stApp {
        background-color: #2E7D32 !important;
        background-image: url("https://www.agroperiferia.com.ar/wp-content/uploads/2021/01/soja-1.jpg");
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(255, 255, 255, 0.7) !important; }
    .titulo { color: #1B5E20; text-align: center; font-size: 35px; font-weight: 900; }
    label, p, span { color: #000 !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background-color: #1B5E20 !important; color: white !important; height: 50px; font-weight: bold; }
    .btn-wa { display: block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; text-decoration: none; }
    .reporte { background-color: white; padding: 15px; border-radius: 10px; border-left: 8px solid #1B5E20; color: black; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.write("---")

opcion = st.radio("ORIGEN DE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR AHORA'):
        with st.spinner('Procesando...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Sos Agrónomo. Analizá y receta corto usando: {VADEMECUM}"
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte'><b>📋 INFORME:</b><br><br>{res.text}</div>", unsafe_allow_html=True)
                    break
                except: continue

if 'rep' in st.session_state:
    txt = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={txt}' target='_blank' class='btn-wa'>📲 ENVIAR A WHATSAPP</a>", unsafe_allow_html=True)

st.write("San Jorge, SF")
