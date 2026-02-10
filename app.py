import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- CSS PARA FONDO DE SOJA Y TEXTO NEGRO ---
st.markdown("""
    <style>
    /* 1. Fondo de pantalla: Campo de soja */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                          url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    [data-testid="stHeader"], [data-testid="stMainBlockContainer"] {
        background-color: transparent !important;
    }

    /* 2. Título de la App */
    .titulo-app {
        color: #ffffff;
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        text-shadow: 2px 2px 4px #000000;
        margin-bottom: 5px;
    }

    /* 3. Estilo de los Botones */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        border: 2px solid #ffffff !important;
    }

    /* 4. CAJA DE RESULTADO: Letra negra sobre fondo blanco */
    .caja-informe {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        color: #000000 !important; /* TEXTO NEGRO */
        font-size: 18px;
        line-height: 1.5;
        border-left: 12px solid #2E7D32;
        margin-top: 20px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }

    /* Letras blancas para las opciones */
    label, p {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO DE LA APP ---
st.markdown("<div class='titulo-app'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# Selector de origen
modo = st.radio("SELECCIONÁ ORIGEN:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if modo == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("CARGAR FOTO DEL LOTE", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 GENERAR DIAGNÓSTICO TÉCNICO'):
        with st.spinner('Procesando datos agrícolas...'):
            try:
                # Buscamos el modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                
                prompt = "Actuá como un Ingeniero Agrónomo experto. Analizá la imagen y respondé con este formato: 1- DIAGNÓSTICO, 2- CAUSA, 3- TRATAMIENTO."
                response = model.generate_content([prompt, img])
                
                # Despliegue del informe con texto negro
                st.markdown(f"""
                    <div class='caja-informe'>
                        <h3 style='color: #2E7D32; margin-top:0;'>✅ INFORME DEL ESPECIALISTA</h3>
                        {response.text.replace('\n', '<br>')}
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error técnico: {e}")

st.markdown("<br><p style='text-align:center; opacity:0.8; font-size:12px;'>Desarrollado para La Clementina v4.8</p>", unsafe_allow_html=True)
