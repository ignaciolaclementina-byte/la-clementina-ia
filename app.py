import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. LLAVE Y DATOS (Tu API Key está OK)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
PRODUCTOS = ", ".join(PRECIOS_USD.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DE LA APP
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.6); }
    .informe-box { background-color: white; padding: 25px; border-radius: 15px; color: #1e1e1e !important; border-left: 10px solid #1b5e20; margin-top: 20px; }
    h1, label, p, span { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; border-radius: 12px; height: 50px; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Cargar imagen", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("El Ingeniero IA está analizando el lote..."):
            try:
                # CONFIGURACIÓN ESTABLE (Solución al 404)
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Analiza la foto de {cul} en {est}. Diagnostica plagas/malezas y receta solo: {PRODUCTOS}. Formato: 'Producto: Dosis l/ha'."
                
                # Proceso de la IA (Corregido error de corchetes [])
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Cálculo de costos
                costo_ha = 0.0
                lista_compra = []
                for p, precio in PRECIOS_USD.items():
                    if p.lower() in informe.lower():
                        match = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                        if match:
                            d = float(match.group(1).replace(',', '.'))
                            if d > 10: d /= 1000 # cm3 a litros
                            costo_ha += (d * precio)
                            lista_compra.append(f"• {p}: {d*has:.1f} lts")

                # MOSTRAR RESULTADOS
                st.markdown("<div class='informe-box'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#1b5e20; margin-top:0;'>📋 REPORTE AGRONÓMICO</h3>", unsafe_allow_html=True)
                st.write(f"<div style='color:black;'>{informe}</div>", unsafe_allow_html=True)
                
                if lista_compra:
                    st.markdown("<hr style='border: 0.5px solid #ccc;'>")
                    st.markdown("<b style='color:black;'>INSUMOS TOTALES PARA EL LOTE:</b>", unsafe_allow_html=True)
                    for item in lista_compra:
                        st.write(f"<div style='color:black;'>{item}</div>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>INVERSIÓN: USD {costo_ha * has:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.session_state['wa_msg'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cul} ({has} ha)\n\n{informe}\n\n💰 *Inversión: USD {costo_ha * has:.2f}*"

            except Exception as e:
                # Corregido el error de la línea 93 (unterminated string)
                st.error(f"Error técnico: {e}")

# 4. BOTÓN WHATSAPP
