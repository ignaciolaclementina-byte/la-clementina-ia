import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
from datetime import datetime
import re

# 1. LISTA DE PRECIOS (USD)
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.45); }
    .titulo { color: #ffffff; text-align: center; font-size: 40px; font-weight: 900; text-shadow: 2px 2px 4px #000; }
    label, p, span { color: #ffffff !important; font-weight: 700 !important; }
    .reporte-box { background-color: white; padding: 25px; border-radius: 15px; color: black !important; border-left: 12px solid #1b5e20; }
    .stButton>button { width: 100%; background: linear-gradient(145deg, #1b5e20, #2e7d32) !important; color: white !important; height: 60px; font-size: 20px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ DE ENTRADA
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#2ecc71 !important;'>San Jorge • Inteligencia y Gestión</p>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    cultivo = st.selectbox("CULTIVO:", ["Soja", "Maíz", "Trigo", "Barbecho"])
with col2:
    estado = st.text_input("ESTADO:", "V4")
with col3:
    has = st.number_input("HECTÁREAS:", min_value=1.0, value=50.0, step=1.0)

foto = st.camera_input("") or st.file_uploader("Subir foto", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR LOTE Y CALCULAR COMPRA'):
        with st.spinner('Calculando logística y costos...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    prompt = f"Agrónomo de San Jorge. Analizá {cultivo} {estado}. Diagnóstico y receta de: {VADEMECUM}. Poné: 'Dosis: X l/ha' o 'Dosis: X cm3/ha'."
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    
                    # Lógica de cálculos
                    costo_ha = 0.0
                    detalles_compra = []
                    
                    for prod, precio in PRECIOS.items():
                        if prod.lower() in informe.lower():
                            match = re.search(rf"{prod}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                            if match:
                                dosis = float(match.group(1).replace(',', '.'))
                                if dosis > 10: dosis = dosis / 1000 # de cm3 a lts
                                
                                total_prod = dosis * has
                                subtotal_usd = dosis * precio
                                costo_ha += subtotal_usd
                                items_compra = f"• **{prod}**: {total_prod:.1f} lts totales (USD {subtotal_usd * has:.2f})"
                                detalles_compra.append(items_compra)

                    st.markdown(f"""
                        <div class="reporte-box">
                            <h3 style="color: #1b5e20;">📋 INFORME Y LOGÍSTICA ({has} ha)</h3>
                            <p style="color: #333 !important;">{informe.replace(chr(10), '<br>')}</p>
                            <hr>
                            <h4 style="color: #c0392b;">🛒 NECESIDAD DE COMPRA TOTAL:</h4>
                            <p style="color: #333 !important;">{"<br>".join(detalles_compra)}</p>
                            <h2 style="color: #1b5e20; text-align:right; margin-top:10px;">TOTAL LOTE: USD {(costo_ha * has):.2f}</h2>
                            <p style="text-align:right; color: #666 !important;">Costo por Ha: USD {costo_ha:.2f}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state['rep_full'] = f"{informe}\n\n🛒 *COMPRA PARA {has} HA:*\n" + "\n".join(detalles_compra) + f"\n\n💰 *TOTAL LOTE: USD {(costo_ha * has):.2f}*"
                    break
                except: continue

if 'rep_full' in st.session_state:
    txt_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n📍 {cultivo} ({has} ha)\n\n{st.session_state['rep_full
