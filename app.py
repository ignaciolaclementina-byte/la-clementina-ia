import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TU NUEVA CLAVE MAESTRA
NUEVA_KEY = "AIzaSyAvgxhXGnDNWiD9VatHcekC0R9DQIBf77I"
VADEMECUM = """
ADHERENTES: Optimizer, Rizo Spray, Break Thru, Fulltec.
BIOESTIMULANTES: YaraVita, Nutrition Grow, Fosfito, Howler.
FUNGICIDAS: Cripton SC, Cripton Xpro.
HERBICIDAS: Round Up, 2,4-D, Atrazina, Paraquat.
INSECTICIDAS: Solomon, Bifentrin, Starkle, Ampligo.
"""

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
    }
    .titulo { color: white; text-align: center; font-size: 32px; font-weight: bold; text-shadow: 2px 2px 4px black; }
    .reporte-box { background: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #2e7d32; margin-top: 20px; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #2e7d32 !important; color: white !important; font-weight: bold; height: 50px; }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 3. LÓGICA DE CARGA
has = st.number_input("HECTÁREAS DEL LOTE:", min_value=1.0, value=100.0)
foto = st.file_uploader("Subí foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR AHORA'):
        with st.spinner('El Ingeniero IA está redactando el informe...'):
            try:
                genai.configure(api_key=NUEVA_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Actuá como Ingeniero Agrónomo. Analizá la imagen. Identificá el problema y recetá productos de: {VADEMECUM}. Sé muy profesional y detallado."
                
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Guardamos en sesión para evitar que desaparezca
                st.session_state['reporte'] = informe
                
            except Exception as e:
                st.error(f"Error de conexión: {str(e)}")

# 4. MOSTRAR RESULTADO Y WHATSAPP (Aquí estaba el error de tu captura)
if 'reporte' in st.session_state:
    # Mostrar el informe en la caja blanca
    st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{st.session_state['reporte'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
    
    # Botón de WhatsApp corregido
    texto_wa = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA*\n\n{st.session_state['reporte']}")
    link_wa = f"https://wa.me/543406649346?text={texto_wa}"
    
    st.markdown(f"""
        <a href="{link_wa}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366; color:white; padding:15px; border-radius:25px; text-align:center; font-weight:bold; margin-top:20px;">
                📲 ENVIAR INFOR
