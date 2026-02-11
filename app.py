import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES (PARA NO QUEDARTE SIN CUOTA)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", 
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. CSS REFORZADO PARA EL FONDO DE SOJA
st.markdown("""
    <style>
    /* Forzamos el fondo en todos los contenedores posibles */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?q=80&w=2070&auto=format&fit=crop") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    .titulo { color: white; text-align: center; font-size: 34px; font-weight: bold; text-shadow: 3px 3px 6px black; }
    .sub-titulo { color: #f0f0f0; text-align: center; font-size: 18px; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }

    /* TRADUCCIONES */
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold;
        height: 50px; font-size: 18px; border: none;
    }
    .btn-whatsapp {
        display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; text-align: center; width: 100%;
    }
    .stExpander { background-color: rgba(0,0,0,0.7) !important; border-radius: 15px; border: 1px solid white; }
    .stExpander p { color: white !important; }
    div[data-testid="stWidgetLabel"] p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-titulo'>San Jorge, Santa Fe</div>", unsafe_allow_html=True)

# 4. AYUDA CÁMARA
with st.expander("❓ ¿PROBLEMAS CON LA CÁMARA? TOCÁ ACÁ"):
    st.write("1. Permiso: Tocá el candado 🔒 al lado del link y activá 'Cámara'.")
    st.write("2. WhatsApp: Tocá los 3 puntitos (⋮) arriba y elegí 'Abrir en el navegador'.")
    st.write("3. Plan B: Sacá la foto normal y usá '📁 GALERÍA'.")

# 5. CARGA DE IMAGEN
opcion = st.radio("SELECCIONÁ:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    # CORREGIDO: Lista de tipos bien cerrada para evitar SyntaxError
    foto = st.file_uploader("Subí una imagen para analizar", type=["jpg", "png", "jpeg"])

if foto:
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando lote...'):
            listo = False
            for api_key in CLAVES:
                try:
                    genai.configure(api_key=api_key)
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt = f"Actuá como Ingeniero Agrónomo de San Jorge. Diagnóstico y receta comercial usando: {VADEMECUM_CLEMENTINA}. En español."
                    response = model.generate_content([prompt, img_ready])
                    
                    st.session_state['reporte_actual'] = response.text
                    inf_h = response.text.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{inf_h}</div>", unsafe_allow_html=True)
                    listo = True
                    break
                except Exception as e:
                    if "429" in str(e): continue # Si hay error de cuota, pasa a la otra llave
                    else: break
            if not listo:
                st.error("⚠️ Cuota agotada en ambas cuentas. Reintentá en 1 minuto.")

# 6. WHATSAPP
if 'reporte_actual' in st.session_state:
    t_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    st.markdown(f"<a href='https://wa.me/?text={t_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 7. PIE DE PÁGINA
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; background-color: rgba(0,0,0,0.7); padding: 15px; border-radius: 15px;'>
        <p style='color: white; font-size: 12px; margin: 0;'>Desarrollado por</p>
        <p style='color: #4CAF50; font-size: 20px; font-weight: bold; margin: 0;'>IGNACIO DIAZ</p>
    </div>
    """, unsafe_allow_html=True)
