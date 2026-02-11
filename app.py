import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. TUS DATOS (Verificados)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO NÍTIDO (Sin caracteres fantasma)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .titulo { color: white; text-align: center; font-size: 35px; font-weight: 900; text-shadow: 2px 2px 4px #000; }
    .reporte-box { background: white; padding: 20px; border-radius: 15px; color: black !important; border-left: 8px solid #2e7d32; }
    .stButton>button { background-color: #2e7d32 !important; color: white !important; font-weight: bold; border-radius: 10px; height: 50px; }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# 3. INTERFAZ
has = st.number_input("HECTÁREAS DEL LOTE:", min_value=1.0, value=100.0)
opcion = st.radio("ORIGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR Y CALCULAR INVERSIÓN'):
        # Reiniciamos el reporte por si había uno viejo
        if 'rep' in st.session_state: del st.session_state['rep']
        
        with st.spinner('Analizando con el Ingeniero IA...'):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    # Forzamos la versión estable del modelo
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"Actúa como agrónomo. Analiza la imagen. Identifica problemas y receta productos de esta lista: {VADEMECUM}. Especifica la dosis por hectárea."
                    
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    
                    # Cálculo de Inversión
                    total_usd = 0.0
                    for p, precio in PRECIOS_USD.items():
                        if p.lower() in informe.lower():
                            m = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                            dosis = float(m.group(1).replace(',', '.')) if m else 0.5
                            if dosis > 10: dosis /= 1000
                            total_usd += (dosis * precio * has)

                    st.session_state['rep'] = informe
                    st.session_state['total'] = total_usd
                    
                    st.markdown(f"<div class='reporte-box'><b>📋 REPORTE:</b><br><br>{informe}<br><hr><b>💰 INVERSIÓN: USD {total_usd:.2f}</b></div>", unsafe_allow_html=True)
                    exito = True
                    break
                except Exception as e:
                    continue
            
            if not exito:
                st.error("La IA está ocupada o las claves expiraron. Reintentá en un minuto.")

# 4. WHATSAPP
if 'rep' in st.session_state:
    texto_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n💰 Inversión: USD {st.session_state['total']:.2f}\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' style='text-decoration:none;'><div style='background:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;'>📲 ENVIAR POR WHATSAPP</div></a>", unsafe_allow_html=True)
