import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES (CON RESPALDO)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]

VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. EL SKIN DEFINITIVO (FORZANDO ELIMINACIÓN DE FONDO NEGRO)
st.markdown("""
    <style>
    /* Eliminamos el color negro de todas las capas de Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main, [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    
    /* Ponemos la imagen de soja en la capa base */
    html, body, [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Ajustamos el texto para que se lea perfecto */
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: bold; text-shadow: 3px 3px 6px black; margin-top: -50px; }
    .sub { color: #f0f0f0; text-align: center; font-size: 18px; text-shadow: 2px 2px 4px black; margin-bottom: 30px; }
    
    /* Forzamos que etiquetas y radio buttons sean blancos */
    label, p, span, .stMarkdown { color: white !important; font-weight: bold !important; text-shadow: 1px 1px 3px black; }

    /* Caja de diagnóstico blanca para contraste total */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95) !important; padding: 25px; border-radius: 20px; 
        color: black !important; border-left: 12px solid #2E7D32; box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }
    .reporte-box * { color: black !important; text-shadow: none !important; }

    /* Botones Pro */
    .stButton>button { width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; height: 55px; border: 2px solid white; font-size: 18px; }
    .btn-wa { display: block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; text-decoration: none; text-align: center; border: 2px solid white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONTENIDO DE LA APP
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

with st.expander("❓ AYUDA CON LA CÁMARA"):
    st.write("1. Tocá el candado 🔒 arriba y dale permiso a la cámara.")
    st.write("2. Si estás en WhatsApp, usá 'Abrir en navegador'.")

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Corregido el error de la línea 82 (SyntaxError)
    foto = st.file_uploader("Buscá tu imagen en el celu", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando cultivo...'):
            listo = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    # Usamos el modelo flash directo para evitar el error 404
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como Agrónomo experto de San Jorge. Da un diagnóstico y receta comercial usando este vademécum: {VADEMECUM}. Sé breve y profesional. Respuesta en español."
                    res = model.generate_content([prompt, img])
                    
                    st.session_state['rep'] = res.text
                    html = res.text.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO DEL ANÁLISIS:</b><br><br>{html}</div>", unsafe_allow_html=True)
                    listo = True
                    break
                except:
                    continue
            if not listo:
                st.error("⚠️ Cuota agotada. Esperá 1 minuto.")

if 'rep' in st.session_state:
    link = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR REPORTE POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center'>Desarrollado por <b>IGNACIO DIAZ</b></p>", unsafe_allow_html=True)
