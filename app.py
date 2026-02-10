import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. SEGURIDAD Y CONEXIÓN
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# 2. LISTA DE PRODUCTOS ACTUALIZADA
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray (Extremo, Integrum, Sulfo Dry, Corrector, Antiespuma), Break Thru, Fulltec, Alquimia, Rizospray Zen, Tropgreen, Powersil.
BIOESTIMULANTES: YaraVita Croplift Bio, Nutrition Grow, Fosfito de Potasio, Eurofit, Howler, Vitagrow, Taisei, Top Zinc Max, Fertiactyl GZ.
FUNGICIDAS: Cripton SC, Cripton Xpro SC.
HERBICIDAS: Round Up (Control Max, Top), 2,4-D (Ethil Exil, Deferon Hexil, Micro Emulsion, Powerspray LV, ME 30% Sigma), Atrazina, Paraquat, Terbutilazina, Acetoclor (Harness), Fomesafen, Fierce, Cletodim, Picloram (Toram), Mayoral, Pyroxasulfone, Imazapir, Capaz, Brodal, Dicamba, Gemmit Top, Diclosulam (Bigua).
INSECTICIDAS: Abamectina, Solomon, Bifentrin, Starkle, Ampligo, Lambda Microencapsulada, Boomer, Eminent, Belt 480 SC, Idaten, Imidacloprid, Clorantraniliprole, Decis Forte, Galil, Actellic Plus, Fosfuro Aluminio, Coragen.
SILO BOLSA: Ipesa, Silox.
"""

# 3. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="La Clementina IA", layout="centered")

# 4. DISEÑO VISUAL (CSS)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; margin-bottom: 5px;}
    .reporte-box {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        margin-top: 20px;
        font-size: 17px;
    }
    .reporte-box * { color: black !important; }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    
    .stButton>button {
        width: 100%;
        border-radius: 30px;
        height: 3.5em;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid white !important;
    }

    .btn-whatsapp {
        display: inline-block;
        background-color: #25D366;
        color: white !important;
        padding: 15px 20px;
        border-radius: 30px;
        text-decoration: none;
        font-weight: bold;
        text-align: center;
        margin-top: 15px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 5. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 6. INTERFAZ
opcion = st.radio("SELECCIONÁ ORIGEN:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subir imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 ANALIZAR Y RECETAR'):
        with st.spinner('Analizando muestra...'):
            try:
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                
                prompt = f"""
                Actuá como un Ingeniero Agrónomo experto de San Jorge. 
                Diagnóstico y receta comercial usando prioritariamente: {VADEMECUM_CLEMENTINA}.
                """
                
                response = model.generate_content([prompt, img])
                texto_puro = response.text
                texto_html = texto_puro.replace('\n', '<br>')
                
                st.session_state['reporte_actual'] = texto_puro
                
                st.markdown(f"""
                    <div class='reporte-box'>
                        <b style='font-size: 20px; color: #2E7D32 !important;'>📋 INFORME TÉCNICO:</b><br><br>
                        {texto_html}
                    </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")

# 7. BOTÓN WHATSAPP
if 'reporte_actual' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *CONSULTA LA CLEMENTINA IA*\n\n{st.session_state['reporte_actual']}")
    link_wa = f"https://wa.me/?text={texto_wa}"
    
    st.markdown(f"""
        <a href="{link_wa}" target="_blank" class="btn-whatsapp">
            📲 ENVIAR RECETA POR WHATSAPP
        </a>
    """, unsafe_allow_html=True)

# 8. FIRMA FINAL (Sin <br> de texto)
st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 20px; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p style='color: white; font-size: 12px; margin: 0; opacity: 0.8;'>Creado y desarrollado por</p>
        <p style='color: #4CAF50; font-size: 18px; font-weight: bold; margin: 0;'>IGNACIO DIAZ</p>
        <p style='color: gray; font-size: 10px;'>Tecnología Agrícola • San Jorge, Santa Fe</p>
    </div>
    """, unsafe_allow_html=True)
