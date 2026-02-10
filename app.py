import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", layout="centered")

# --- CSS MEJORADO PARA CONTRASTE ALTO ---
st.markdown("""
    <style>
    /* 1. Fondo de pantalla: Campo de soja con oscurecimiento fuerte para resaltar el frente */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
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
        font-size: 36px;
        font-weight: bold;
        text-shadow: 3px 3px 6px #000000;
        margin-top: -30px;
    }

    /* 3. Estilo de los Botones: Verde Agrónomo */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.8em;
        background-color: #2E7D32 !important;
        color: white !important;
        font-weight: bold;
        font-size: 18px;
        border: 2px solid #ffffff !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
    }

    /* 4. LA CLAVE: CAJA DE RESULTADO (Letra negra, fondo blanco puro) */
    .caja-informe {
        background-color: #ffffff !important;
        padding: 30px;
        border-radius: 15px;
        color: #000000 !important; /* NEGRO PURO */
        font-size: 19px; /* Un poco más grande para el campo */
        line-height: 1.6;
        border-left: 15px solid #1B5E20;
        margin-top: 25px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.6);
    }

    /* Títulos dentro de la caja blanca */
    .caja-informe b, .caja-informe strong {
        color: #000000 !important;
    }

    /* Etiquetas de control en blanco con sombra */
    label, p {
        color: white !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px black;
        font-size: 17px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO DE LA APP ---
st.markdown("<div class='titulo-app'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Diagnóstico Experto - San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# Selector de origen con estilo
st.markdown("<br>", unsafe_allow_html=True)
modo = st.radio("SELECCIONÁ CÓMO CARGAR LA MUESTRA:", ["📸 Cámara", "📁 Galería"], horizontal=True)

if modo == "📸 Cámara":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("CARGAR FOTO DEL LOTE", type=["jpg", "png", "jpeg"])

if foto:
    st.image(foto, use_container_width=True, caption="Imagen seleccionada")
    
    if st.button('🚀 GENERAR DIAGNÓSTICO TÉCNICO'):
        with st.spinner('Consultando al especialista virtual...'):
            try:
                # Inicialización del modelo
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                
                # Prompt optimizado para respuestas claras
                prompt = "Sos un Ingeniero Agrónomo experto de Argentina. Analizá esta imagen de cultivo y entregá: 1. DIAGNÓSTICO CLARO, 2. CAUSA DEL PROBLEMA, 3. TRATAMIENTO SUGERIDO."
                response = model.generate_content([prompt, img])
                
                # Despliegue con reemplazo de saltos de línea para HTML
                resultado_formateado = response.text.replace('\n', '<br>')
                
                st.markdown(f"""
                    <div class='caja-informe'>
                        <h2 style='color: #1B5E20; margin-top:0; font-size:24px;'>✅ INFORME DEL ESPECIALISTA</h2>
                        <hr style='border: 1px solid #eee;'>
                        {resultado_formateado}
                    </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Error técnico: {e}")

st.markdown("<br><hr style='opacity:0.3;'><p style='text-align:center; opacity:0.8; font-size:12px;'>La Clementina v5.0 - San Jorge</p>", unsafe_allow_html=True)
