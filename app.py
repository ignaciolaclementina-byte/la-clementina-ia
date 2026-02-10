import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de Página
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# 2. Estilo Visual
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.9);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label { color: white !important; text-align: center; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; height: 50px; font-weight: bold; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# 3. Login
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.markdown("<h1>🔐 Acceso</h1>", unsafe_allow_html=True)
    if st.text_input("Contraseña:", type="password") == "clementina2024":
        if st.button("INGRESAR"):
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. Aplicación
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("📸 Subir foto del cultivo", type=['jpg', 'jpeg', 'png'])

if archivo:
    img = Image.open(archivo)
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Consultando con el motor de La Clementina..."):
            try:
                # CONEXIÓN CORREGIDA
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # CAMBIO CLAVE: Quitamos el prefijo 'models/' que está dando el error 404
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = "Sos un experto agrónomo. Analizá esta imagen de cultivo y da: 1-Diagnóstico, 2-Producto recomendado (Solomon, Starkle, Belt, u Optimizer), 3-Dosis."
                
                # Generar contenido
                response = model.generate_content([prompt, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.write(response.text)
                else:
                    st.error("La IA no devolvió una respuesta clara.")
                    
            except Exception as e:
                # Si el error persiste, probamos con el nombre alternativo del modelo
                try:
                    model = genai.GenerativeModel('gemini-pro-vision')
                    response = model.generate_content([prompt, img])
                    st.success("✅ RECOMENDACIÓN (Vía Pro Vision):")
                    st.write(response.text)
                except:
                    st.error(f"Error técnico detallado: {str(e)}")
