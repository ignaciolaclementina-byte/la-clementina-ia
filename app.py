import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS LLAVES (CON RESPALDO)
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

# 2. CSS "BRUTO" PARA ELIMINAR EL FONDO NEGRO Y PONER SOJA
st.markdown("""
    <style>
    /* Forzamos el fondo en todas las capas de Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), 
                          url("https://images.unsplash.com/photo-1559813595-8854d7c3d8a1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    
    /* Hacemos que el texto de los widgets se lea bien */
    .stMarkdown, p, span, label { color: white !important; font-weight: bold; text-shadow: 1px 1px 3px black; }
    .titulo { color: white; text-align: center; font-size: 34px; font-weight: bold; text-shadow: 3px 3px 6px black; margin-bottom: 0; }
    .sub-titulo { color: #f0f0f0; text-align: center; font-size: 18px; margin-bottom: 20px; text-shadow: 2px 2px 4px black; }

    /* Estilo para el cuadro de diagnóstico (Blanco para que se lea perfecto) */
    .reporte-box {
        background-color: white !important;
        padding: 20px; border-radius: 15px; color: black !important; border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .reporte-box * { color: black !important; text-shadow: none !important; }
    
    /* Botones Pro */
    .stButton>button {
        width: 100%; border-radius: 30px; background-color: #2E7D32 !important; color: white !important; font-weight: bold;
        height: 55px; font-size: 18px; border: 2px solid white;
    }
    .btn-whatsapp {
        display: inline-block; background-color: #25D366; color: white !important; padding: 15px; border-radius: 30px; 
        text-decoration: none; font-weight: bold; text-align: center; width: 100%; border: 2px solid white;
    }
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

# 5. CARGA DE IMAGEN (ERROR CORREGIDO)
opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("") 
else:
    # AQUÍ ESTABA EL ERROR: Ahora está cerrado correctamente
    foto = st.file_uploader("Subí una imagen para analizar", type=["jpg", "png", "jpeg"])

if foto:
    img_ready = Image.open(foto).convert('RGB')
    st.image(img_ready, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Un Agrónomo virtual está analizando...'):
            listo = False
            for api_key in CLAVES:
                try:
                    genai.configure(api_key=api_key)
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if not modelos: continue
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt = f"Actuá como Ingeniero Agrónomo de San Jorge. Diagnóstico y receta comercial detallada usando: {VADEMECUM_CLEMENTINA}. Respuesta en español."
                    response = model.generate_content([prompt, img_ready])
                    
                    st.session_state['reporte_actual'] = response.text
                    inf_h = response.text.replace('\n', '<br>')
                    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{inf_h}</div>", unsafe_allow_html=True)
                    listo = True
                    break
                except Exception as e:
                    if "429" in str(e): continue
                    else: break
            if not listo:
                st.error("⚠️ Sistema saturado. Reintentá en 1 minuto.")

# 6. WHATSAPP
if 'reporte_actual' in st.session_state:
    t_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    st.markdown(f"<a href='https://wa.me/?text={t_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 7. FIRMA
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; background-color: rgba(0,0,0,0.6); padding: 10px; border-radius: 10px;'><p style='margin:0'>Desarrollado por <b>IGNACIO DIAZ</b></p></div>", unsafe_allow_html=True)
