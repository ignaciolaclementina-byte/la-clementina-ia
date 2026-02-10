import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de API
genai.configure(api_key="AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw")

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="La Clementina IA", page_icon="🚜", layout="wide")

# --- ESTILOS PERSONALIZADOS (CSS) ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #2e7d32;
        color: white;
        height: 3em;
        font-size: 18px;
    }
    .status-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .header-style {
        color: #1b5e20;
        font-family: 'Arial';
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (Menú de Selección) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2950/2950151.png", width=100)
    st.title("Configuración")
    opcion = st.radio("Seleccionar Fuente:", ["📸 Cámara", "📁 Galería"])
    st.info("Sacá la foto bien de cerca a la hoja o síntoma para mejor precisión.")

# --- CUERPO PRINCIPAL ---
st.markdown("<h1 class='header-style'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Diagnóstico Inteligente de Cultivos</p>", unsafe_allow_html=True)
st.divider()

col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.subheader("Entrada de Imagen")
    if opcion == "📸 Cámara":
        archivo = st.camera_input("Enfocá el síntoma")
    else:
        archivo = st.file_uploader("Subí una foto del lote", type=["jpg", "png", "jpeg"])

with col_der:
    st.subheader("Resultado del Análisis")
    if archivo:
        st.image(archivo, caption="Muestra Seleccionada", use_container_width=True)
        
        if st.button('🚀 ANALIZAR AHORA'):
            with st.spinner('Consultando con el Agrónomo Virtual...'):
                try:
                    # Lógica de procesamiento
                    img = Image.open(archivo).convert('RGB')
                    img.thumbnail((500, 500))
                    
                    modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    model = genai.GenerativeModel(modelos[0])
                    
                    prompt = "Sos un ingeniero agrónomo. Analizá la imagen y respondé por puntos: 1. Qué tiene. 2. Por qué pasó. 3. Qué aplicar."
                    response = model.generate_content([prompt, img])
                    
                    # Mostrar en una tarjeta linda
                    st.markdown(f"""
                        <div class="status-card">
                            <h3 style="color: #2e7d32; margin-top:0;">✅ Informe Técnico:</h3>
                            {response.text.replace("\n", "<br>")}
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error técnico: {e}")
    else:
        st.warning("Esperando que cargues una imagen para empezar...")

st.divider()
st.caption("© 2026 La Clementina - Gestión Agrícola Inteligente")
