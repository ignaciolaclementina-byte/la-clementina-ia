import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LISTA DE CLAVES (SISTEMA DE RELEVO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", # Tu clave 1
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"  # Tu clave 2
]

# VADEMÉCUM
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO Y TRADUCCIÓN DE BOTONES (CSS)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    
    /* TRADUCCIÓN BOTÓN GALERÍA */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    section[data-testid="stFileUploadDropzone"]:before { content: "Arrastrá tu foto acá o"; color: white; font-weight: bold; margin-bottom: 10px; }

    /* TRADUCCIÓN BOTÓN CÁMARA */
    div[data-testid="stCameraInput"] button { font-size: 0px !important; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
    }

    .btn-whatsapp {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        padding: 15px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 4. INTERFAZ
opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    foto = st.file_uploader("Subí una imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando muestra con IA...'):
            exito = False
            # INTENTAR CON CADA CLAVE
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Actuá como un Ingeniero Agrónomo de San Jorge. Diagnóstico y receta comercial usando: {VADEMECUM_CLEMENTINA}. Respuesta en español."
                    
                    response = model.generate_content([prompt, img])
                    informe = response.text
                    
                    st.session_state['reporte_actual'] = informe
                    informe_web = informe.replace('\n', '<br>')
                    
                    st.markdown(f"""
                        <div class='reporte-box'>
                            <b style='font-size: 20px;'>📋 INFORME TÉCNICO:</b><br><br>
                            {informe_web}
                        </div>
                    """, unsafe_allow_html=True)
                    exito = True
                    break # Si funcionó, salimos del bucle de claves
                except Exception as e:
                    if "429" in str(e):
                        continue # Si es error de cuota, prueba la siguiente clave
                    else:
                        st.error(f"Error técnico: {e}")
                        break
            
            if not exito:
                st.error("⚠️ Cuota agotada en todas las cuentas. Esperá 1 minuto y probá de nuevo.")

# 5. WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_puro = st.session_state['reporte_actual']
    texto_codificado = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{texto_puro}")
    link_wa = f"https://wa.me/?text={texto_codificado}"
    st.markdown(f"<a href='{link_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 6. FIRMA FINAL IGNACIO DIAZ
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p style='color
