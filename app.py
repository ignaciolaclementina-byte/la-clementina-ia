import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DATOS
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO AGRO-ESTABLE
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.pexels.com/photos/235925/pexels-photo-235925.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.65); /* Filtro para ver bien el texto */
    }
    .titulo { color: #004d00; text-align: center; font-size: 38px; font-weight: 900; text-shadow: 2px 2px 4px white; margin-top: -40px; }
    label, p, span, div.stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button { 
        width: 100%; border-radius: 15px; background-color: #1B5E20 !important; 
        color: white !important; height: 60px; font-size: 20px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px;
    }
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 12px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí la imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ESCANEAR Y RECETAR'):
        with st.spinner('Analizando cultivo y calculando dosis...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # PROMPT MEJORADO PARA DOSIS
                    prompt = f"""Sos un Ingeniero Agrónomo experto de San Jorge. 
                    Analizá la imagen y da un diagnóstico preciso. 
                    Recetá usando SOLO estos productos: {VADEMECUM}.
                    IMPORTANTE: Incluí dosis estimadas (ej: litros/ha o cm3/ha) según la severidad que veas."""
                    
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME DEL INGENIERO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    break
                except: continue

# 4. ENVÍO WHATSAPP
if 'rep' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *INFORME LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' class='btn-wa'>📲 MANDAR RECETA AL WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; font-size: 12px;'>Desarrollado por Ignacio Diaz</p>", unsafe_allow_html=True)
