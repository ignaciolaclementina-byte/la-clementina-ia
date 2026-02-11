import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. PARÁMETROS FIJOS (CON TU CLAVE PROPIA)
CLAVE = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = "Optimizer, Rizo Spray, YaraVita, Cripton, Round Up, 2,4-D, Solomon, Ampligo"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL NITIDO
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .card { background-color: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 10px solid #1b5e20; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
    label, p, span { color: white !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; border-radius: 10px; height: 50px; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# Controles
c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # CONFIGURACIÓN DEFINITIVA
                genai.configure(api_key=CLAVE)
                # Forzamos el modelo estable para evitar el error 404
                model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                
                # Pedido a la IA (Asegurando cierre de comillas)
                prompt = f"Actúa como agrónomo. Analiza esta foto de {cul} en {est}. Diagnóstico de plagas y manchas. Receta solo: {VADEMECUM}. Usa 'Dosis: X l/ha'."
                
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Cálculo de costos y litros
                costo_ha = 0.0
                compra = []
                for p, prec in PRECIOS.items():
                    if p.lower() in informe.lower():
                        match = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                        if match:
                            d = float(match.group(1).replace(',', '.'))
                            if d > 10: d = d / 1000 # Convierte cm3 a litros
                            costo_ha += (d * prec)
                            compra.append(f"• {p}: {d*has:.1f} lts totales")

                # Resultado en pantalla
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#1b5e20;'>📋 INFORME {cul}</h3>", unsafe_allow_html=True)
                st.write(informe)
                st.markdown("<hr>", unsafe_allow_html=True)
                if compra:
                    st.markdown("<b>COMPRA RECOMENDADA:</b>", unsafe_allow_html=True)
                    for item in compra: st.write(item)
                st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>TOTAL: USD {costo_ha*has:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Guardamos el mensaje para WhatsApp
                st.session_state['msg'] = f"🚜 *LA CLEMENTINA IA*\n📍 {cul} ({has} ha)\n\n{informe}\n\n💰 *TOTAL: USD {costo_ha*has:.2f}*"
                
            except Exception as e:
                st.error(f"Error técnico: {e}. Reintentá en un momento.")

# Botón WhatsApp
if 'msg' in st.session_state:
    url_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(st.session_state['msg'])}"
    st.markdown(f"""
        <a href="{url_wa}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:10px; border:2px solid white;">
                📲 ENVIAR AL WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
