import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES (CON RESPALDO)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]

VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. SKIN: FORZANDO ELIMINACIÓN DE GRIS/NEGRO
st.markdown("""
    <style>
    /* Eliminamos el fondo gris de Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background: none !important;
        background-color: #1a2e1a !important; /* Verde oscuro de respaldo */
    }
    
    /* Ponemos la imagen de soja como base total */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=1920&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Títulos con sombra para que 'salten' de la pantalla */
    .titulo { color: white; text-align: center; font-size: 38px; font-weight: bold; text-shadow: 4px 4px 8px black; margin-top: -40px; }
    .sub { color: #e0e0e0; text-align: center; font-size: 20px; text-shadow: 2px 2px 5px black; margin-bottom: 30px; }
    
    /* Forzamos texto blanco en todo el menú */
    label, p, span, .stMarkdown { color: white !important; font-weight: bold !important; text-shadow: 1px 1px 3px black; }

    /* Caja de resultados: Blanca para que se lea perfecto */
    .reporte-box {
        background-color: rgba(255, 255, 255, 0.98) !important; padding: 25px; border-radius: 20px; 
        color: black !important; border-left: 15px solid #2E7D32; box-shadow: 0px 10px 30px rgba(0,0,0,0.7);
    }
    .reporte-box * { color: black !important; text-shadow: none !important; }

    /* Botones Profesionales */
    .stButton>button { width: 100%; border-radius: 35px; background-color: #2E7D32 !important; color: white !important; height: 60px; border: 3px solid white; font-size: 20px; font-weight: bold; }
    .btn-wa { display: block; background-color: #25D366; color: white !important; padding: 18px; border-radius: 35px; text-decoration: none; text-align: center; border: 3px solid white; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ PRINCIPAL
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

with st.expander("❓ AYUDA CON LA CÁMARA"):
    st.write("1. Dale permiso a la cámara en el candado 🔒 de arriba.")
    st.write("2. En WhatsApp, usá 'Abrir en navegador' para que no falle.")

opcion = st.radio("ORIGEN DE IMAGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    # Corrección definitiva de syntax en esta línea
    foto = st.file_uploader("Subí tu imagen desde el equipo", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO PROFESIONAL'):
        with st.spinner('Un Ingeniero Agrónomo virtual está analizando...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como Ingeniero Agrónomo de San Jorge. Da un diagnóstico y receta comercial usando: {VADEMECUM}. Sé técnico y directo. Respuesta en español."
                    res = model.generate_content([prompt, img])
                    
                    st.session_state['rep'] = res.text
                    html_res = res.text.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{html_res}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except:
                    continue
            if not exito:
                st.error("⚠️ Sistema saturado. Reintentá en un minuto.")

if 'rep' in st.session_state:
    link_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/?text={link_wa}' target='_blank' class='btn-wa'>📲 ENVIAR REPORTE POR WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center'>Desarrollado por <b>IGNACIO DIAZ</b> - San Jorge, SF</p>", unsafe_allow_html=True)
