import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TU NUEVA API KEY (Cargada y lista)
NUEVA_KEY = "AIzaSyAvgxhXGnDNWiD9VatHcekC0R9DQIBf77I"
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO PROFESIONAL
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: 900; text-shadow: 2px 2px 4px #000; }
    .reporte-box { background: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #2e7d32; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; height: 55px; border-radius: 12px; border: 2px solid white; }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 3. INTERFAZ
has = st.number_input("HECTÁREAS DEL LOTE:", min_value=1.0, value=100.0)
archivo = st.file_uploader("Subir foto del lote para analizar", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 INICIAR ANÁLISIS AHORA'):
        with st.spinner('El Ingeniero IA está analizando con la nueva llave...'):
            try:
                # CONFIGURACIÓN LIMPIA
                genai.configure(api_key=NUEVA_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""Sos Ingeniero Agrónomo. Analizá la imagen. 
                1. Identificá malezas o plagas. 
                2. Recetá productos de esta lista: {VADEMECUM}. 
                3. Recomendá la dosis por hectárea."""
                
                # Pedir respuesta a la IA
                res = model.generate_content([prompt, img])
                informe_final = res.text
                
                # Mostrar el reporte
                st.markdown(f"<div class='reporte-box'><b>📋 REPORTE DEL LOTE:</b><br><br>{informe_final}</div>", unsafe_allow_html=True)
                st.session_state['reporte_ok'] = informe_final

            except Exception as e:
                st.error(f"Hubo un problema con la nueva llave: {str(e)}")

# 4. WHATSAPP
if 'reporte_ok' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *REPORTE LA CLEMENTINA IA*\n\n{st.session_state['reporte_ok']}")
    st.markdown(f"""
        <a href="https://wa.me/{MI_NUMERO}?text={texto_wa}" target="_blank" style="text-decoration:none;">
            <div style="background:#25D366; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold; margin-top:20px; border: 2px solid white;">
                📲 ENVIAR REPORTE AL WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
