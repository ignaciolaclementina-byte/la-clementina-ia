import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (SISTEMA DE RESPALDO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", # Clave 1
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"  # Clave 2
]

# VADEMÉCUM CLEMENTINA (ACTUALIZADO)
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
        background-attachment: fixed !important;
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
        padding: 25px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        height: 50px;
        font-size: 18px;
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
        margin-top: 10px;
    }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>Asesoría Agronómica • San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 4. INTERFAZ
opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    foto = st.file_uploader("Subí una imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR INFORME TÉCNICO'):
        with st.spinner('Análisis en curso...'):
            exito = False
            for api_key in CLAVES:
                try:
                    genai.configure(api_key=api_key)
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue 
                        
                    model = genai.GenerativeModel(modelos[0])
                    
                    # PROMPT SENIOR MEJORADO
                    prompt = f"""
                    Actuá como un Ingeniero Agrónomo senior de San Jorge, Santa Fe. 
                    Analizá la imagen y generá un informe con este formato:

                    1. **DIAGNÓSTICO**: Sé directo (ej: "Ataque de Isoca detectado"). Explicá brevemente qué ves.
                    2. **RECETA CLEMENTINA (Mezcla de Tanque)**: Armá una combinación lógica usando: {VADEMECUM_CLEMENTINA}. 
                       - Debés incluir: Producto principal + Adherente recomendado + Bioestimulante para el estrés.
                    3. **RECOMENDACIÓN TÉCNICA**: Un consejo de aplicación (clima, calidad de agua o velocidad).

                    Usá un tono profesional pero cercano, de colega a colega.
                    """
                    
                    response = model.generate_content([prompt, img_ready])
                    informe = response.text
                    
                    st.session_state['reporte_actual'] = informe
                    informe_html = informe.replace('\n', '<br>')
                    
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME PARA EL PRODUCTOR:</b><br><br>{informe_html}</div>", unsafe_allow_html=True)
                    exito = True
                    break 
                    
                except Exception:
                    continue

            if not exito:
                st.error("⚠️ El sistema está saturado. Reintentá en 1 minuto.")

# 5. WHATSAPP (CON NÚMERO ESPECÍFICO)
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *
