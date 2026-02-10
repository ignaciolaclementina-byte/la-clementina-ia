import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilos (Fondo de Soja)
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    border: 2px solid #4CAF50;
    padding: 2rem;
    border-radius: 15px;
}
h1, h3, p, label, .stMarkdown { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; text-shadow: 2px 2px 4px #000000; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; border: none; }
</style>
""", unsafe_allow_html=True)

# 3. Sesión de Usuario
if "entró" not in st.session_state:
    st.session_state.entró = False

if not st.session_state.entró:
    st.title("🔐 Acceso La Clementina")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("INGRESAR"):
        if clave == "clementina2024":
            st.session_state.entró = True
            st.rerun()
        else:
            st.error("Error de clave")
    st.stop()

# 4. Interfaz Principal
st.title("🚜 LA CLEMENTINA IA")
st.write("### Diagnóstico con Stock 2026")

opcion = st.radio("Seleccione origen:", ["📸 Cámara", "📁 Galería"], horizontal=True)
archivo = None

if opcion == "📸 Cámara":
    archivo = st.camera_input("Sacar foto")
else:
    archivo = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # REVISIÓN DE API KEY
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("❌ No se encontró la GOOGLE_API_KEY en los Secrets de Streamlit.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # Usamos el modelo más estable
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                productos = "STOCK 2026: Solomon, Starkle, Ampligo, Zariva, Lambda, Boomer, Eminent, Belt, Idaten. COADYUVANTES: Optimizer, Rizo Spray Extremo, Integrum, Fulltec, Zen."
                pedido = f"Sos ingeniero agronomo de La Clementina. Analiza la imagen. Diagnostica el problema. Recomienda solo productos de este stock: {productos}"
                
                # Generar contenido
                response = model.generate_content([pedido, img])
                
                if response.text:
                    st.success("✅ DICTAMEN TÉCNICO:")
                    st.write(response.text)
                else:
                    st.warning("La IA no pudo generar una respuesta clara. Intente con otra foto.")
                    
            except Exception as e:
                st.error(f"❌ Error de conexión: {str(e)}")
                st.info("Asegurate de que la API KEY sea válida y tenga permisos para Gemini.")
