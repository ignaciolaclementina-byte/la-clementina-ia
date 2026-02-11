import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. PARAMETROS FIJOS
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "Optimizer, Rizo Spray, YaraVita, Cripton, Round Up, 2,4-D, Solomon, Ampligo"
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL (FONDO NITIDO)
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.45); }
    .main-title { color: white; text-align: center; font-size: 35px; font-weight: 900; text-shadow: 2px 2px 4px black; }
    .card { background-color: white; padding: 20px; border-radius: 15px; color: black !important; border-left: 10px solid #1b5e20; }
    label, p, span { color: white !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='main-title'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#2ecc71 !important;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a: cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col_b: estado = st.text_input("ESTADO", "V4")
with col_c: hectareas = st.number_input("HAS", min_value=1.0, value=1.0)

archivo = st.camera_input("") or st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("Analizando..."):
            exito = False
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    # Prompt ultra directo para evitar errores de la IA
                    prompt = f"Actúa como agrónomo. Analiza {cultivo} en {estado}. Diagnóstico y receta usando solo: {VADEMECUM}. Usa formato 'Dosis: X l/ha'."
                    response = model.generate_content([prompt, img])
                    informe_ia = response.text
                    
                    # Cálculo de Costos
                    costo_por_ha = 0.0
                    detalle_logistica = []
                    for prod, precio in PRECIOS.items():
                        if prod.lower() in informe_ia.lower():
                            match = re.search(rf"{prod}.*?(\d+[.,]?\d*)", informe_ia, re.IGNORECASE)
                            if match:
                                d = float(match.group(1).replace(',', '.'))
                                if d > 10: d = d / 1000 # de cm3 a litros
                                
                                subtotal_item = d * precio
                                costo_por_ha += subtotal_item
                                detalle_logistica.append(f"• {prod}: {d*hectareas:.2f} lts totales")

                    costo_total_lote = costo_por_ha * hectareas
                    
                    # Mostrar resultados en pantalla
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='color:#1b5e20;'>📋 INFORME PARA {hectareas} HAS</h3>", unsafe_allow_html=True)
                    st.write(informe_ia)
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("<b>COMPRA RECOMENDADA:</b>", unsafe_allow_html=True)
                    for item in detalle_logistica: st.write(item)
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>TOTAL: USD {costo_total_lote:.2f}</h2>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Guardar para WhatsApp
                    msg_wa = f"🚜 *LA CLEMENTINA IA*\n📍 {cultivo} ({hectareas} ha)\n\n{informe_ia}\n\n💰 *TOTAL: USD {costo_total_lote:.2f}*"
                    st.session_state['wa_final'] = msg_wa
                    exito = True
                    break
                except Exception:
                    continue
            
            if not exito:
                st.error("Error técnico. Verificá tu conexión o las claves API.")

# 4. BOTON WHATSAPP
if 'wa_final' in st.session_state:
    url_wa = f"https://wa.me/{MI_NUMERO}?text={urllib.parse.quote(st.session_state['wa_final'])}"
    st.markdown(f"""
        <a href="{url_wa}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:10px; border:1px solid white;">
                📲 MANDAR A WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
