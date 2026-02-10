import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. SEGURIDAD
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 2. VADEMÉCUM
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec, Alquimia, Tropgreen.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler, Vitagrow.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat, Harness, Fierce, Cletodim.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo, Belt, Coragen.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 3. DISEÑO Y TRADUCCIÓN DE BOTONES (CSS)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    
    /* TRUCO PARA TRADUCIR EL BOTÓN DE CARGA */
    section[data-testid="stFileUploadDropzone"] button {
        font-size: 0px !important;
    }
    section[data-testid="stFileUploadDropzone"] button:after {
        content: "BUSCAR IMAGEN";
        font-size: 16px !important;
    }
    section[data-testid="stFileUploadDropzone"] span {
        display: none;
    }
    section[data-testid="stFileUploadDropzone"]:before {
        content: "Arrastrá tu foto acá o";
        color: white;
        font-weight: bold;
        margin-bottom: 10px;
    }

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

# 4. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 5. INTERFAZ EN CASTELLANO
opcion = st.radio("SELECCIONÁ DE DÓNDE VIENE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("Sacá la foto del lote")
else:
    # Etiqueta traducida
    foto = st.file_uploader("Subí una imagen (JPG, PNG o JPEG)", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO'):
        with st.spinner('Analizando muestra...'):
            try:
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                img = Image.open(foto).convert('RGB')
                
                prompt = f"""
                Actuá como un Ingeniero Agrónomo de San Jorge. 
                Diagnóstico y receta comercial usando: {VADEMECUM_CLEMENTINA}.
                Respuesta siempre en español castellano.
                """
                
                response = model.generate_content([prompt, img])
                texto_puro = response.text
                st.session_state['reporte_actual'] = texto_puro
                
                st.markdown(f"""
                    <div class='reporte-box'>
                        <b style='font-size: 20px;'>📋 INFORME TÉCNICO:</b><br><br>
                        {texto_puro.replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

# 6. WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    link_wa = f"https://wa.me/?text={texto_wa}"
    st.markdown(f"<a href='{link_wa}' target='_blank' class='btn-whatsapp'>📲 ENVIAR POR WHATSAPP</a>", unsafe_allow_html=True)

# 7. TU FIRMA (Sin errores de texto)
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p style='color: white; font-size: 12px; margin: 0;'>Creado y desarrollado por</p>
        <p style='color: #4CAF50; font-size: 18px; font-weight: bold; margin: 0;'>IGNACIO DIAZ</p>
        <p style='color: gray; font-size: 10px;'>San Jorge, Santa Fe</p>
    </div>
    """, unsafe_allow_html=True)
