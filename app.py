import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DATOS (Sin tocar nada acá)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DEL FONDO (Enlace corto y seguro)
st.markdown("""
    <style>
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1615811361269-6c8788109039?q=80&w=1920&auto=format&fit=crop");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Panel blanco semitransparente para que se lea bien */
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.5);
    }

    .titulo { color: #1B5E20; text-align: center; font-size: 40px; font-weight: 900; text-shadow: 2px 2px 4px white; margin-top: -30px; }
    .sub { color: #2E7D32; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; text-shadow: 1px 1px 2px white; }
    
    label, p, span, div.stMarkdown { color: #000000 !important; font-weight: 800 !important; font-size: 16px; }

    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #1B5E20 !important; 
        color: white !important; height: 60px; font-size: 20px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px; margin-top: 20px;
    }
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 10px; 
        color: black !important; border-left: 10px solid #1B5E20; box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. PANTALLA PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("ORIGEN DE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subí tu foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR CULTIVO'):
        with st.spinner('Consultando al Ingeniero IA...'):
            exito = False
            for key in CLAVES:
                try:
                    # ACÁ ESTABA EL ERROR ANTES, AHORA ESTÁ ARREGLADO:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Sos un Agrónomo experto de campo argentino. Analizá la imagen. Diagnóstico y receta usando solo: {VADEMECUM}. Sé breve y técnico."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except: continue

# 4. BOTÓN DE WHATSAPP
if 'rep' in st.session_state:
    texto = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto}' target='_blank' class='btn-wa'>📲 ENVIAR A MI WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center;'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
