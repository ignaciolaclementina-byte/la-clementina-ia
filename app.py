import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (SISTEMA DE RESPALDO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", # Clave 1
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"  # Clave 2
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

# 2. DISEÑO CON FONDO ANTERIOR (CSS)
st.markdown("""
    <style>
    /* Fondo de campo con filtro oscuro */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center center !important;
        background-attachment: fixed !important;
    }
    
    .titulo { color: white; text-align: center; font-size: 38px; font-weight: 900; text-shadow: 2px 2px 8px #000000; margin-top: -20px; }
    .sub-txt { color: #ffffff !important; text-align: center; font-size: 18px; font-weight: bold; text-shadow: 1px 1px 3px #000000; }
    
    /* Etiquetas y textos en blanco para legibilidad */
    label, p, span, div.stMarkdown { color: #ffffff !important; font-weight: 700 !important; }

    /* TRADUCCIÓN BOTÓN GALERÍA */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    section[data-testid="stFileUploadDropzone"]:before { content: "Arrastrá tu foto acá o"; color: white; font-weight: bold; margin-bottom: 10px; }

    /* TRADUCCIÓN BOTÓN CÁMARA */
    div[data-testid="stCameraInput"] button { font-size: 0px !important; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    /* Caja de reporte BLANCA para contraste */
    .reporte-box {
        background-color: white !important;
        padding: 25px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
    }
    .reporte-box * { color: black !important; }
    
    /* Botón verde fuerte */
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        height: 55px;
        border: 2px solid white;
    }

    .btn-whatsapp {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        padding: 15px;
        border-radius: 30px;
        text-decoration: none;
        text-align: center;
        font-weight: bold;
        width: 100%;
        border: 2px solid white;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p class='sub-txt'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 4. INTERFAZ
opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    foto = st.file_uploader("Subí una imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando muestra...'):
            exito = False
            for api_key in CLAVES:
                try:
                    genai.configure(api_key=api_key)
                    
                    # Detección de modelo disponible (evita 404)
                    modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos_disponibles:
                        continue 
                        
                    model = genai.GenerativeModel(modelos_disponibles[0])
                    
                    prompt = f"Actuá como un Ingeniero Agrónomo de San Jorge. Diagnóstico y receta comercial usando: {VADEMECUM_CLEMENTINA}. Respuesta en español."
                    
                    response = model.generate_content([prompt, img_ready])
                    informe = response.text
                    
                    st.session_state['reporte_actual'] = informe
                    informe_html = informe.replace('\n', '<br>')
                    
                    st.markdown(f"""
                        <div class='reporte-box'>
                            <b style='font-size: 20px;'>📋 INFORME TÉCNICO:</b><br><br>
                            {informe_html}
                        </div>
                    """, unsafe_allow_html=True)
                    exito = True
                    break 
                    
                except Exception as e:
                    if "429" in str(e):
                        continue
                    else:
                        continue

            if not exito:
                st.error("⚠️ Sistema saturado. Reintentá en 1 minuto.")

# 5. WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    link_wa = f"https://wa.me/543406649346?text={texto_wa}"
    st.markdown(f"<a href='{link
