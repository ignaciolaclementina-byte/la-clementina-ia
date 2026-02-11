import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN (Tu API Key está perfecta)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = ", ".join(PRECIOS_USD.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .card { background-color: white; padding: 20px; border-radius: 10px; color: black !important; border-left: 8px solid #1b5e20; }
    h1, label, p, span { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; border: none; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. DATOS DE ENTRADA
col1, col2, col3 = st.columns(3)
with col1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2: est = st.text_input("ESTADO", "R3")
with col3: has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # LA SOLUCIÓN AL 404: Configurar sin v1beta
                genai.configure(api_key=API_KEY)
                # Usamos el nombre del modelo directo
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Como agrónomo, analiza esta foto de {cul} en {est}. Diagnóstico de plagas y receta de: {VADEMECUM}. Formato: 'Producto: Dosis l/ha'."
                
                # Generar contenido (Corregido el error de corchetes)
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Cálculo de costos
                costo_ha = 0.0
                compra = []
                for p, precio in PRECIOS_USD.items():
                    if p.lower() in informe.lower():
                        match = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                        if match:
                            dosis = float(match.group(1).replace(',', '.'))
                            if dosis > 10: dosis /= 1000 # de cm3 a lts
                            costo_ha += (dosis * precio)
                            compra.append(f"• {p}: {dosis * has:.1f} lts")

                # MOSTRAR RESULTADOS
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#1b5e20;'>📋 REPORTE TÉCNICO</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:black;'>{informe}</p>", unsafe_allow_html=True)
                
                if compra:
                    st.markdown("<hr style='border-top: 1px solid #ccc;'>")
                    st.markdown("<b style='color:black;'>COMPRA SUGERIDA:</b>", unsafe_allow_html=True)
                    for item in compra:
                        st.markdown(f"<p style='color:black;'>{item}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>INVERSIÓN: USD {costo_ha * has:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Guardar para WhatsApp
                st.session_state['reporte'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cul} ({has} ha)\n\n{informe}\n\n💰 *Total: USD {costo_ha * has:.2f}*"

            except Exception as e:
                st.error(f"Error técnico: {e}. Reintentá en un momento.")

# 4. BOTÓN WHATSAPP
if 'reporte' in st.session_state:
    texto_wa = urllib.parse.quote(st.session_state['reporte'])
    st.markdown(f"""
        <a href="https://wa.me/543406649346?text={texto_wa}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:15px; border: 2px solid white;">
                📲 ENVIAR REPORTE AL WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
