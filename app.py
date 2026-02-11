import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS LLAVES DE API
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw",
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
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
    
    /* TRADUCCIÓN BOTONES */
    section[data-testid="stFileUploadDropzone"] button:after { content: "BUSCAR IMAGEN"; font-size: 16px !important; }
    section[data-testid="stFileUploadDropzone"] span { display: none; }
    div[data-testid="stCameraInput"] button:after { content: "TOMAR FOTO"; font-size: 16px !important; }

    .reporte-box {
        background-color: white !important;
        padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32;
    }
    .reporte-box * { color: black !important; }
    
    .stButton>button {
        width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold;
    }
    .btn-whatsapp {
        display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; text-align: center; width: 100%;
    }
    /* ESTILO AYUDA */
    .stExpander { background-color: rgba(255,255,255,0.1); border-radius: 15px; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# --- NUEVA SECCIÓN DE AYUDA ---
with st.expander("❓ ¿PROBLEMAS CON LA CÁMARA? TOCÁ ACÁ"):
    st.markdown("""
    1. **Permitir acceso:** Tocá el **candado 🔒** arriba al lado del link y activá la cámara.
    2. **Desde WhatsApp:** Si lo abriste por mensaje, tocá los **3 puntitos (⋮)** arriba a la derecha y elegí **'Abrir en el navegador'** o **'Abrir en Chrome'**.
    3. **Plan B:** Sacá la foto con tu cámara normal y usá la opción **'📁 GALERÍA'**.
    """)

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
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt = f"Actuá como un Ingeniero Agrónomo de San Jorge. Diagnóstico y receta comercial usando: {VADEMECUM_CLEMENTINA}. Respuesta en español."
                    response = model.generate_content([prompt, img_ready])
                    informe = response.text
                    
                    st.session_state['reporte_actual'] = informe
                    informe_html = informe.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{informe_html}</div>", unsafe_allow_html=True)
                    exito = True
                    break
                except Exception as e:
                    if "429" in str(e): continue
                    else: break
            if not exito:
                st.error("⚠️ Sistema saturado. Esperá 1 minuto.")

# 5. WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    st.markdown(f"<a href='https://wa.me/?text={texto_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 6. FIRMA
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;'><p style='color: white; font-size: 12px;'>Desarrollado por</p><p style='color: #4CAF50; font-size: 18px; font-weight: bold;'>IGNACIO DIAZ</p></div>", unsafe_allow_html=True)
