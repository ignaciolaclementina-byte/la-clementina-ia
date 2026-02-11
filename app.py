import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DATOS TÉCNICOS
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO "PAMPA" (Fondo de lote real y alta legibilidad)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.7); /* Filtro para que el sol no tape el texto */
    }
    .titulo { color: #004d00; text-align: center; font-size: 38px; font-weight: 900; text-shadow: 2px 2px 4px white; margin-top: -30px; }
    label, p, span, div.stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #1B5E20 !important; 
        color: white !important; height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px; margin-top: 10px;
    }
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 10px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA IMAGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ESCANEAR Y CALCULAR DOSIS'):
        with st.spinner('El Ingeniero IA está analizando el lote...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    # PROMPT DE ALTA PRECISIÓN
                    prompt = f"""Sos un Ingeniero Agrónomo senior de San Jorge, Santa Fe. 
                    Analizá la imagen adjunta. Identificá malezas, plagas o deficiencias.
                    Recetá una solución usando ÚNICAMENTE estos productos: {VADEMECUM}.
                    IMPORTANTE: Para cada producto mencionado, especificá la DOSIS RECOMENDADA por hectárea (l/ha o cm3/ha) basándote en la severidad que observás en la foto. 
                    Sé técnico, directo y profesional."""
                    
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 REPORTE TÉCNICO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    break
                except: continue

# 4. BOTÓN WHATSAPP
if 'rep' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' class='btn-wa'>📲 ENVIAR REPORTE AL WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; font-size: 11px;'>Desarrollado por Ignacio Diaz</p>", unsafe_allow_html=True)
