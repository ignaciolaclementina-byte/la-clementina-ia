import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. EL SKIN DEFINITIVO: FUERZA BLANCO Y QUITA GRIS
st.markdown("""
    <style>
    /* Esto mata el gris de fondo de una vez por todas */
    .stApp { background-color: white !important; }
    [data-testid="stAppViewContainer"] { background-color: white !important; }
    
    /* Imagen de soja solo como un detalle superior suave */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop");
        background-size: cover;
        z-index: -1;
    }

    /* Estilo Agrónomo: Verde y Negro para que se lea bien */
    .titulo { color: #1B5E20; text-align: center; font-size: 32px; font-weight: bold; margin-bottom: 0; }
    .sub { color: #2E7D32; text-align: center; font-size: 18px; margin-bottom: 20px; }
    label, p, span { color: #1a1a1a !important; font-weight: bold !important; }

    /* Botones y Cajas */
    .stButton>button { width: 100%; border-radius: 10px; background-color: #2E7D32 !important; color: white !important; height: 50px; border: none; }
    .reporte-box { background-color: #f9f9f9 !important; padding: 20px; border-radius: 10px; color: black !important; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Aseguramos que no falte ninguna comilla aquí
    foto = st.file_uploader("Elegí una imagen", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR LOTE'):
        with st.spinner('Procesando...'):
            try:
                genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(["Actuá como agrónomo de San Jorge, analizá la imagen y da receta técnica.", img])
                st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO:</b><br><br>{res.text}</div>", unsafe_allow_html=True)
            except:
                st.error("Error de conexión. Reintentá.")
