import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
from datetime import datetime
import re

# 1. CONFIGURACIÓN DE PRECIOS Y CLAVES
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO "FULL HD" (Fondo nítido con overlay oscuro sutil)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] {
        background-color: rgba(0, 0, 0, 0.4);
    }
    .titulo { color: #ffffff; text-align: center; font-size: 40px; font-weight: 900; text-shadow: 2px 2px 8px #000; margin-bottom: 0; }
    .sub { color: #2ecc71 !important; text-align: center; font-weight: bold; font-size: 18px; margin-bottom: 20px; }
    label, p, span { color: white !important; font-weight: 700 !important; }
    .reporte-card { background-color: white; padding: 25px; border-radius: 15px; border-left: 10px solid #1b5e20; color: black !important; }
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(to right, #1b5e20, #2e7d32) !important; color: white !important; font-weight: bold; height: 55px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ DE USUARIO
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub'>San Jorge, Santa Fe • v42.0</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "V4")
with c3: has = st.number_input("HECTÁREAS", min_value=1.0, value=50.0)

foto = st.camera_input("") or st.file_uploader("Cargar imagen", type=["jpg","png","jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR DIAGNÓSTICO Y COSTOS"):
        with st.spinner("El Ingeniero IA está analizando el lote..."):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Sos Agrónomo en San Jorge. Analizá {cul} {est}. Usá solo: {VADEMECUM}. Decí diagnóstico y dosis exacta como 'Dosis: X l/ha'."
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    
                    # Cálculo de costos y totales
                    costo_h = 0.0
                    lista_compra = []
                    for p, prec in PRECIOS.items():
                        if p.lower() in informe.lower():
                            match = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                            if match:
                                d = float(match.group(1).replace(',','.'))
                                if d > 10: d = d / 1000 # cm3 a litros
                                sub_u = d * prec
                                costo_h += sub_u
                                lista_compra.append(f"• {p}: {d*has:.1f} litros totales")
                    
                    # Mostrar Reporte
                    st.markdown(f"""
                        <div class="reporte-card">
                            <h3 style="color:#1b5e20;">📋 REPORTE TÉCNICO</h3>
                            <p style="color:#333 !important; font-weight: 400 !important;">{informe.replace(chr(10), '<br>')}</p>
                            <hr>
                            <h4 style="color:#c0392b;">🛒 LOGÍSTICA PARA {has} HA:</h4>
                            <p style="color:#333 !important; font-weight: 400 !important;">{"<br>".join(lista_compra)}</p>
