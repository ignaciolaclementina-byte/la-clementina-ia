import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TU LLAVE MAESTRA
NUEVA_KEY = "AIzaSyAvgxhXGnDNWiD9VatHcekC0R9DQIBf77I"
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton SC, Cripton Xpro. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO LIMPIO
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    .reporte-box { background: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #2e7d32; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e7d32 !important; color: white !important; font-weight: bold; height: 50px; }
    label, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
has = st.number_input("HECTÁREAS:", min_value=1.0, value=100.0)
foto = st.file_uploader("Subí foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 INICIAR ANÁLISIS'):
        with st.spinner('El Ingeniero IA está redactando...'):
            try:
                genai.configure(api_key=NUEVA_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Actuá como Ingeniero Agrónomo. Analizá esta foto de cultivo. Identificá la enfermedad o plaga y recetá productos de: {VADEMECUM}. Sé técnico."
                
                res = model.generate_content([prompt, img])
                st.session_state['reporte_final'] = res.text
            except Exception as e:
                st.error(f"Error: {str(e)}")

# 4. RESULTADO (Sin errores de comillas triples)
if 'reporte_final' in st.session_state:
    informe = st.session_state['reporte_final']
    
    # Caja de texto blanca
    st.markdown("<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>" + informe.replace("\n", "<br>") + "</div>", unsafe_allow_html=True)
    
    # Botón WhatsApp
    texto_wa = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA*\n\n{informe}")
    link_wa = f"https://wa.me/{MI_NUMERO}?text={texto_wa}"
    
    st.markdown(f"<a href='{link_wa}' target='_blank' style='text-decoration:none;'><div style='background:#25D366; color:white; padding:15px; border-radius:25px; text-align:center; font-weight:bold; margin-top:20px;'>📲 ENVIAR POR WHATSAPP</div></a>", unsafe_allow_html=True)

# Firma
st.markdown("<p style='text-align:center; font-size:10px; color:gray; margin-top:50px;'>Desarrollado por Ignacio Diaz</p>", unsafe_allow_html=True)
