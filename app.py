import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES DE API
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", 
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

# VADEMÉCUM DE PRODUCTOS
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILOS VISUALES
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    
    /* Botones de carga en español */
    section[data-testid="stFileUploadDropzone"] button { font-size: 0px !important; }
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    
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
        margin-top: 10px;
    }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 4. INTERFAZ DE CARGA
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
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue
                    
                    model = genai.GenerativeModel(modelos[0])
                    
                    # PROMPT OPTIMIZADO CON EL MENSAJE COMERCIAL
                    prompt = f"""
                    Actuá como un Ingeniero Agrónomo senior de San Jorge, Santa Fe. 
                    Analizá la imagen y generá un informe profesional con este formato:

                    1. **DIAGNÓSTICO**: Explicación técnica de lo observado.
                    2. **RECETA CLEMENTINA**: Mezcla de tanque recomendada usando productos de: {VADEMECUM_CLEMENTINA}.
                    3. **RECOMENDACIÓN TÉCNICA**: Consejos de aplicación (clima, boquillas o calidad de agua).

                    Finalizá SIEMPRE con esta frase exacta:
                    "📌 Recordá que todos los productos mencionados se pueden comprar en **LA CLEMENTINA - SAN JORGE, SANTA FE**."
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
                st.error("⚠️ Sistema saturado. Por favor, reintentá en un minuto.")

# 5. BOTÓN WHATSAPP CON NÚMERO DIRECTO
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA - INFORME TÉCNICO*\n\n{st.session_state['reporte_actual']}")
    # Enlace directo a tu número
    link_wa = f"https://wa.me/543406649346?text={texto_wa}"
    st.markdown(f"<a href='{link_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 6. FIRMA
st.markdown("<br><br><div style='text-align: center; color: white; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;'>Desarrollado por <b>IGNACIO DIAZ</b></div>", unsafe_allow_html=True)
