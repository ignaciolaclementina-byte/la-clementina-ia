import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API (SISTEMA DE RESPALDO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", # Clave 1
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"  # Clave 2
]

# VADEMÉCUM COMPLETO
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
    
    /* TRADUCCIONES DE BOTONES */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    section[data-testid="stFileUploadDropzone"]:before { content: "Seleccioná tu foto o"; color: white; font-weight: bold; margin-bottom: 10px; }

    div[data-testid="stCameraInput"] button { font-size: 0px !important; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: white !important;
        padding: 25px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        height: 50px;
    }

    .btn-whatsapp {
        display: block;
        background-color: #25D366;
        color: white !important;
        padding: 15px;
        border-radius: 30px;
        text-decoration: none;
        text-align: center;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
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
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Conectando con el Ingeniero IA...'):
            exito = False
            for api_key in CLAVES:
                try:
                    genai.configure(api_key=api_key)
                    
                    # Buscamos modelo disponible (Solución definitiva al 404)
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue
                    
                    # Preferimos gemini-1.5-flash si está disponible
                    modelo_nombre = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in modelos else modelos[0]
                    model = genai.GenerativeModel(modelo_nombre)
                    
                    prompt = f"""Sos un Ingeniero Agrónomo senior de San Jorge, Santa Fe. 
                    Analizá la imagen. Identificá malezas, plagas o deficiencias.
                    Recetá una solución usando únicamente estos productos: {VADEMECUM_CLEMENTINA}.
                    Dá la dosis recomendada. Respuesta técnica y directa."""
                    
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
                    continue

            if not exito:
                st.error("⚠️ Sistema saturado. Esperá un minuto e intentá de nuevo.")

# 5. WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    st.markdown(f"<a href='https://wa.me/?text={texto_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 6. FIRMA FINAL
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p style='color: white; font-size: 12px; margin: 0;'>Creado y desarrollado por</p>
        <p style='color: #4CAF50; font-size: 18px; font-weight: bold; margin: 0;'>IGNACIO DIAZ</p>
        <p style='color: gray; font-size: 10px;'>Tecnología Agrícola • San Jorge, Santa Fe</p>
    </div>
    """,
