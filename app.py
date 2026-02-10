import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- LISTA DE PRODUCTOS CARGADA (Basada en tu Excel) ---
VADEMECUM_CLEMENTINA = """
ADHERENTES: Optimizer, Rizo Spray (Extremo, Integrum, Sulfo Dry, Corrector, Antiespuma), Break Thru, Fulltec, Alquimia, Rizospray Zen, Tropgreen, Powersil.
BIOESTIMULANTES: YaraVita Croplift Bio, Nutrition Grow, Fosfito de Potasio, Eurofit, Howler, Vitagrow, Taisei, Top Zinc Max, Fertiactyl GZ.
FUNGICIDAS: Cripton SC, Cripton Xpro SC.
HERBICIDAS: Round Up (Control Max, Top), 2,4-D (Ethil Exil, Deferon Hexil, Micro Emulsion, Powerspray LV, ME 30% Sigma), Atrazina, Paraquat, Terbutilazina, Acetoclor (Harness), Fomesafen, Fierce, Cletodim, Picloram (Toram), Mayoral, Pyroxasulfone, Imazapir, Capaz, Brodal, Dicamba, Gemmit Top, Diclosulam (Bigua).
INSECTICIDAS: Abamectina, Solomon, Bifentrin, Starkle, Ampligo, Lambda Microencapsulada, Boomer, Eminent, Belt 480 SC, Idaten, Imidacloprid, Clorantraniliprole, Decis Forte, Galil, Actellic Plus, Fosfuro Aluminio, Coragen.
SILO BOLSA: Ipesa, Silox.
"""

st.set_page_config(page_title="La Clementina", layout="centered")

# --- DISEÑO VISUAL ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .titulo { color: white; text-align: center; font-size: 28px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    .reporte-box {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        color: black !important;
        border-left: 12px solid #2E7D32;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
        font-size: 16px;
    }
    .reporte-box b, .reporte-box strong { color: #2E7D32 !important; }
    label, p { color: white !important; font-weight: bold; text-shadow: 1px 1px 2px black; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

opcion = st.radio("Fuente:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if opcion == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subir imagen", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO Y RECETA'):
        with st.spinner('Analizando y consultando stock...'):
            try:
                # Usamos el buscador de modelos que ya te funcionó
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                
                prompt = f"""
                Actuá como un Ingeniero Agrónomo experto de San Jorge, Santa Fe. 
                Analizá la imagen y da:
                1. DIAGNÓSTICO: Qué problema o plaga ves.
                2. CAUSA: Por qué ocurrió.
                3. RECETA COMERCIAL: Recomendá el tratamiento usando específicamente productos de esta lista:
                {VADEMECUM_CLEMENTINA}
                
                Sé directo y profesional.
                """
                
                response = model.generate_content([prompt, img])
                texto_html = response.text.replace('\n', '<br>')
                
                st.markdown(f"""
                    <div class='reporte-box'>
                        <b>📋 INFORME TÉCNICO Y COMERCIAL:</b><br><br>
                        {texto_html}
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<br><p style='text-align:center; color:gray; font-size:10px;'>V.4.0 - Stock Actualizado</p>", unsafe_allow_html=True)
