import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="LA CLEMENTINA IA", page_icon="🚜")

# --- ESTILO VISUAL (FONDO SOJA) ---
st.markdown("""
<style>
.stApp {
    background-image: url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
    background-attachment: fixed;
}
.block-container {
    background-color: rgba(0, 0, 0, 0.85);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #4CAF50;
}
h1, h3, p, label, .stMarkdown { color: white !important; }
h1 { color: #4CAF50 !important; text-align: center; font-weight: bold; }
.stButton>button { background-color: #2e7d32; color: white; width: 100%; font-weight: bold; height: 3em; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h1>🔐 Acceso La Clementina</h1>", unsafe_allow_html=True)
    clave = st.text_input("Contraseña:", type="password")
    if st.button("INGRESAR"):
        if clave == "clementina2024":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.write("### Diagnóstico Experto con Stock 2026")

archivo = st.camera_input("📸 Tomar foto del cultivo")
if not archivo:
    archivo = st.file_uploader("📁 O subir desde galería", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo)
    st.image(img, width=400, caption="Muestra para analizar")
    
    if st.button("🚀 INICIAR DIAGNÓSTICO"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # 1. Validación de la Key
                if "GOOGLE_API_KEY" not in st.secrets:
                    st.error("❌ ERROR: No se encontró la clave GOOGLE_API_KEY en los Secrets.")
                    st.stop()
                
                genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
                
                # 2. Configuración del modelo (Gemini 1.5 Flash es el mejor para fotos)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # 3. Contexto de productos (Extraído de tu lista de precios 2026)
                contexto = """
                Sos un Ingeniero Agrónomo de La Clementina S.A. 
                Analiza la imagen y diagnostica cultivo y problema.
                RECOMIENDA SOLO PRODUCTOS DE NUESTRO STOCK:
                - Insecticidas: Solomon, Bifentrin, Starkle, Ampligo-Zariva, Lambda, Boomer, Eminent, Belt, Idaten.
                - Adherentes: Optimizer, Rizo Spray Extremo, Integrum, Fulltecmax, Alquimia, Rizospray Zen, Tropgreen.
                Brinda diagnóstico y dosis.
                """
                
                # 4. Generación
                response = model.generate_content([contexto, img])
                
                if response.text:
                    st.success("✅ RECOMENDACIÓN TÉCNICA:")
                    st.markdown(response.text)
                else:
                    st.warning("La IA no pudo procesar esta imagen específica. Intenta con otra.")

            except Exception as e:
                st.error(f"❌ ERROR TÉCNICO: {str(e)}")
                st.info("Recomendación: Verifica que la API Key en 'Secrets' no tenga espacios y sea válida.")
