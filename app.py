import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
from datetime import datetime

# 1. DATOS TÉCNICOS
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DE INTERFAZ NITIDA (MODERNA)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(0, 0, 0, 0.45);
    }
    .titulo { color: #ffffff; text-align: center; font-size: 42px; font-weight: 900; text-shadow: 3px 3px 6px #000000; margin-bottom: 5px; }
    .sub-txt { color: #2ecc71 !important; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 25px; }
    
    /* Contenedor tipo Tarjeta */
    .card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 20px;
        color: #1b5e20;
        margin-bottom: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }
    
    label, p, span { color: #ffffff !important; font-weight: 700 !important; }
    .stButton>button { 
        width: 100%; border-radius: 15px; background: linear-gradient(145deg, #1b5e20, #2e7d32) !important; 
        color: white !important; height: 60px; font-size: 22px; border: none; font-weight: bold;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 18px; 
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-txt'>Tecnología de Precisión • San Jorge</div>", unsafe_allow_html=True)

# 4. CONFIGURACIÓN DEL LOTE (NUEVO!)
col1, col2 = st.columns(2)
with col1:
    cultivo = st.selectbox("CULTIVO:", ["Soja", "Maíz", "Trigo", "Barbecho"])
with col2:
    estado = st.text_input("ESTADO (Ej: V3, R1):", "Desconocido")

# 5. CARGA DE IMAGEN
opcion = st.radio("FUENTE DE LA FOTO:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Subir foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 GENERAR RECETA TÉCNICA'):
        with st.spinner('Ingeniero Virtual analizando...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""Sos un Ingeniero Agrónomo experto de San Jorge. 
                    Contexto: Cultivo de {cultivo} en estado {estado}.
                    Analizá la foto y da un diagnóstico preciso.
                    Recetá usando SOLO: {VADEMECUM}.
                    IMPORTANTE: Especificá dosis por hectárea y justificá tu elección basándote en lo que ves en la foto."""
                    
                    res = model.generate_content([prompt, img])
                    st.session_state['rep'] = res.text
                    
                    # Mostrar reporte en "Tarjeta" blanca
                    st.markdown(f"""
                        <div style="background-color: white; padding: 25px; border-radius: 15px; border-left: 12px solid #1b5e20; color: black !important; margin-top: 20px;">
                            <h3 style="color: #1b5e20;">📋 INFORME AGRONÓMICO</h3>
                            <p style="color: #333 !important; font-weight: 400 !important;">{res.text.replace(chr(10), '<br>')}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    break
                except: continue

# 6. BOTÓN WHATSAPP
if 'rep' in st.session_state:
    fecha = datetime.now().strftime("%d/%m/%Y")
    texto_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA - INFORME {fecha}*\n📍 *Lote:* {cultivo} ({estado})\n\n{st.session_state['rep']}")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' class='btn-wa'>📲 MANDAR AL WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; font-size: 11px; opacity: 0.7;'>v37.0 - Desarrollado por Ignacio Diaz</p>", unsafe_allow_html=True)
