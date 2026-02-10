import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración básica
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilos CSS (Fondo de Soja) - Escrito en una sola linea para evitar errores
st.markdown("""<style>.stApp {background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2232&auto=format&fit=crop"); background-size: cover; background-position: center;} .block-container {background-color: rgba(0, 0, 0, 0.9); border: 2px solid #4CAF50; padding: 20px; border-radius: 15px;} h1, h2, h3, p, label, .stMarkdown {color: white !important;} .stButton>button {background-color: #2e7d32; color: white; border-radius: 10px; height: 50px; font-weight: bold; width: 100%;}</style>""", unsafe_allow_html=True)

# 3. Login de Seguridad
if "ingreso" not in st.session_state:
    st.session_state.ingreso = False

if not st.session_state.ingreso:
    st.title("🔒 Acceso La Clementina")
    pwd = st.text_input("Contraseña:", type="password")
    if st.button("ENTRAR AL SISTEMA"):
        if pwd == "clementina2024":
            st.session_state.ingreso = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# 4. Conexión con la IA
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Error de conexión. Verificá la API Key.")
    st.stop()

# 5. Interfaz Principal
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico y Receta Fitosanitaria")

# Pestañas para Cámara y Galería
tab_cam, tab_upl = st.tabs(["📸 USAR CÁMARA", "📁 SUBIR FOTO"])
imagen_final = None

with tab_cam:
    foto = st.camera_input("Tomar foto del cultivo")
    if foto: imagen_final = foto

with tab_upl:
    carga = st.file_uploader("Buscar en galería", type=["jpg", "png", "jpeg"])
    if carga: imagen_final = carga

# 6. Botón de Análisis
if imagen_final:
    st.image(imagen_final, caption="Imagen cargada")
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Consultando stock y diagnosticando..."):
            try:
                # Lista de tus productos (Escribimos todo junto para que no falle)
                mis_productos = "INSECTICIDAS: Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. ADHERENTES: Optimizer, Rizo Spray Extremo, Integrum, Fulltec, Alquimia, Zen, Tropgreen."
                
                # Instrucción para la IA
                pedido = "Sos el ingeniero de La Clementina. Analiza la imagen. Diagnostica el problema. Recomienda tratamiento SOLO usando estos productos de nuestro stock: " + mis_productos
                
                # Procesar imagen
                img_data = Image.open(imagen_final)
                respuesta = model.generate_content([pedido, img_data])
                
                st.success("✅ RECOMENDACIÓN TÉCNICA:")
                st.write(respuesta.text)
                
            except Exception as e:
                st.error(f"Error al analizar: {e}")
