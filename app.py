import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN INICIAL
CLAVE = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = ", ".join(PRECIOS.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .card { background-color: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #1b5e20; }
    label, p, span { color: white !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. INTERFAZ DE USUARIO
c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HAS", min_value=1.0, value=100.0)

# El cargador de archivos que ya estabas usando con éxito
foto = st.camera_input("") or st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("El Ingeniero IA está analizando la imagen..."):
            try:
                # CONFIGURACIÓN ESTABLE - AQUÍ SOLUCIONAMOS EL ERROR 404
                genai.configure(api_key=CLAVE)
                # Forzamos el modelo estable 1.5-flash
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Actúa como agrónomo. Analiza esta foto de {cul} en {est}. Diagnóstico de plagas. Receta solo productos de esta lista: {VADEMECUM}. Usa el formato 'Producto: Dosis l/ha'."
                
                res = model.generate_content([prompt
