import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVES Y VADEMECUM (Sin errores de comillas)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. EL TRUCO DEL SKIN: IMAGEN FLOTANTE
st.markdown("""
    <style>
    /* Ponemos la imagen de soja en una capa que cubra todo el fondo */
    .stApp {
        background: url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed !important;
        background-size: cover !important;
    }
    
    /* Agregamos una capa semi-transparente para que se lea el texto */
    .stApp > header { background: transparent !important; }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(255, 255, 255, 0.4) !important; /* Capa blanca sutil sobre la soja */
    }

    /* Títulos en Verde Oscuro para contraste */
    .titulo { color: #1B5E20; text-align: center; font-size: 34px; font-weight: bold; text-shadow: 2px 2px 4px white; }
    .sub { color: #2E7D32; text-align: center; font-size: 19px; font-weight: bold; text-shadow: 1px 1px 2px white; margin-bottom: 20px; }
    
    /* Texto de controles en Negro */
    label, p, span { color: black !important; font-weight: bold !important; }

    /* Estilo de los Botones */
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #2E7D32 !important; 
        color: white !important; height: 50px; font-size: 18px; border: 2px solid white;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white;
    }
    
    /* Caja de resultados blanca y sólida */
    .reporte-box {
        background-color: white !important; padding: 20px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #2E7D32; box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    .reporte-box * { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Corrección de la línea que te daba SyntaxError antes
    foto = st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            listo = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Ingeniero Agrónomo de San Jorge. Diagnóstico y receta: {VADEMECUM}. Respuesta técnica en español."
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    st.markdown(f"<div class='reporte-box'><b>📋 RESULTADO:</b><br><br>{res.text.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                    listo = True
                    break
                except: continue
            if not listo: st.error("Límite alcanzado, intentá en 1 minuto.")

if 'rep' in st.session_state:
    link = urllib.parse.quote(f"🚜 *CONSULTA CLEMENTINA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link}' target='_blank' class='btn-wa'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)
