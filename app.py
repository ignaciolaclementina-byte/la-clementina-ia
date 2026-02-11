import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. CLAVES ACTUALIZADAS (Es vital que estas funcionen)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO NÍTIDO
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: 900; text-shadow: 2px 2px 4px #000; }
    .reporte-box { background: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #2e7d32; font-size: 16px; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; height: 55px; border-radius: 12px; border: 2px solid white; }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 3. INTERFAZ SIMPLE
has = st.number_input("HECTÁREAS DEL LOTE:", min_value=1.0, value=100.0)
archivo = st.file_uploader("Subir foto del lote", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR Y CALCULAR INVERSIÓN'):
        with st.spinner('Conectando con el Ingeniero IA...'):
            exito = False
            for key in CLAVES:
                try:
                    # CONFIGURACIÓN LIMPIA (Evita el Error 404)
                    genai.configure(api_key=key)
                    # Usamos el modelo sin especificar versión beta para mayor estabilidad
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"Actúa como agrónomo. Analiza la imagen. Identifica plagas/malezas y receta productos de esta lista: {VADEMECUM}. Sé breve."
                    
                    # Generar contenido
                    res = model.generate_content([prompt, img])
                    informe_final = res.text
                    
                    # Mostrar el reporte en la caja blanca para legibilidad
                    st.markdown(f"<div class='reporte-box'><b>📋 REPORTE DEL LOTE:</b><br><br>{informe_final}</div>", unsafe_allow_html=True)
                    st.session_state['reporte_ok'] = informe_final
                    exito = True
                    break 
                except Exception as e:
                    continue
            
            if not exito:
                st.error("Error de acceso. Por favor, verifica que tus API Keys en Google AI Studio estén activas.")

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
