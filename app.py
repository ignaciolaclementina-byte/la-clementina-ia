import streamlit as st
import google.generativeai as genai
from PIL import Image

# Tu clave de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- DISEÑO ULTRA-MÓVIL ---
st.set_page_config(page_title="La Clementina", layout="centered")

st.markdown("""
    <style>
    /* Fondo general */
    .stApp { background-color: #121212; } 
    
    /* Título llamativo */
    .titulo {
        color: #4CAF50;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    
    /* Caja de instrucciones */
    .instrucciones {
        color: #bbbbbb;
        text-align: center;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* Botón de Acción Campero */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 60px;
        background-color: #2E7D32;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: 2px solid #4CAF50;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Caja de Diagnóstico */
    .reporte-box {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #4CAF50;
        color: #ffffff;
        font-size: 16px;
        line-height: 1.5;
        margin-top: 20px;
    }
    
    /* Ocultar elementos innecesarios en móvil */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CONTENIDO ---
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='instrucciones'>Escaneá tu cultivo ahora mismo</div>", unsafe_allow_html=True)

# Selector simple (Menos lugar, más intuitivo)
opcion = st.segmented_control("Fuente de imagen:", ["Cámara", "Galería"], default="Cámara")

if opcion == "Cámara":
    foto = st.camera_input("Enfocá la hoja")
else:
    foto = st.file_uploader("Subí desde el celu", type=["jpg", "png", "jpeg"])

if foto:
    # Mostrar la foto ocupando el ancho justo
    st.image(foto, use_container_width=True)
    
    if st.button('🚀 OBTENER DIAGNÓSTICO'):
        with st.spinner('Analizando...'):
            try:
                # Buscador de modelos (el que te funcionó antes)
                modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                model = genai.GenerativeModel(modelos[0])
                
                img = Image.open(foto).convert('RGB')
                img.thumbnail((600, 600))
                
                prompt = "Sos un agrónomo experto. Da un diagnóstico rápido, la causa y el tratamiento para esta planta."
                response = model.generate_content([prompt, img])
                
                # Resultado en caja oscura para que resalte
                st.markdown(f"<div class='reporte-box'><b>📋 INFORME TÉCNICO:</b><br><br>{response.text}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("<br><p style='text-align:center; color:gray; font-size:10px;'>V.2.0 - San Jorge, Santa Fe</p>", unsafe_allow_html=True)
