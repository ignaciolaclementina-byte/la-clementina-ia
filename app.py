import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN FINAL (CON TU NUEVA CLAVE)
CLAVES = ["AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"]
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = "Optimizer, Rizo Spray, YaraVita, Cripton, Round Up, 2,4-D, Solomon, Ampligo"
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO AGRO-NITIDO
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.45); }
    .card { background-color: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 12px solid #1b5e20; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
    label, p, span { color: white !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background: linear-gradient(145deg, #1b5e20, #2e7d32) !important; color: white !important; font-weight: bold; border-radius: 12px; height: 55px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<h1 style='text-align:center; color:white; text-shadow: 2px 2px 4px black;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#2ecc71 !important; font-weight:bold;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Cargar foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("El Ingeniero IA está analizando el lote..."):
            try:
                genai.configure(api_key=CLAVES[0])
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Actúa como agrónomo experto en San Jorge. Analiza esta foto de {cul} en {est}. Diagnóstico de plagas y enfermedades. Receta SOLO productos de: {VADEMECUM}. Para cada producto poné 'Dosis: X l/ha' o 'Dosis: X cm3/ha'."
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Cálculos
                costo_ha = 0.0
                compra_lista = []
                for p, prec in PRECIOS.items():
                    if p.lower() in informe.lower():
                        m = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                        if m:
                            d = float(m.group(1).replace(',', '.'))
                            if d > 10: d /= 1000 # Convierte cm3 a litros
