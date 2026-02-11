import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
from datetime import datetime
import re

# 1. DATOS TÉCNICOS Y PRECIOS (Ajustables)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

# Precios ref. USD (Podés editarlos acá abajo)
PRECIOS = {
    "Round Up": 8.5, "2,4-D": 10.0, "Cripton": 45.0, 
    "Ampligo": 55.0, "Solomon": 38.0, "Optimizer": 5.0, 
    "Rizo Spray": 4.5, "YaraVita": 12.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO PREMIUM NÍTIDO
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.45); }
    .titulo { color: #ffffff; text-align: center; font-size: 42px; font-weight: 900; text-shadow: 3px 3px 6px #000000; }
    .sub-txt { color: #2ecc71 !important; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 25px; }
    label, p, span { color: #ffffff !important; font-weight: 700 !important; }
    .stButton>button { 
        width: 100%; border-radius: 15px; background: linear-gradient(145deg, #1b5e20, #2e7d32) !important; 
        color: white !important; height: 60px; font-size: 22px; border: none;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 18px; 
        border-radius: 15px; text-decoration: none; text-align: center; font-weight: bold; font-size: 18px;
    }
    .reporte-box { background-color: white; padding: 25px; border-radius: 15px; border-left: 12px solid #1b5e20; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-txt'>Gestión de Costos y Precisión • San Jorge</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    cultivo = st.selectbox("CULTIVO:", ["Soja", "Maíz", "Trigo", "Barbecho"])
with col2:
    estado = st.text_input("ESTADO:", "V3")

foto = st.camera_input("📸 TOMAR FOTO DEL LOTE") or st.file_uploader("📁 SUBIR FOTO", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 CALCULAR DIAGNÓSTICO Y COSTOS'):
        with st.spinner('Ingeniero IA analizando...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""Sos un Agrónomo senior. Analizá esta foto de {cultivo} en {estado}.
                    1. Da diagnóstico técnico.
                    2. Recetá productos de: {VADEMECUM}.
                    3. IMPORTANTE: Poné la dosis como 'Dosis: X l/ha' o 'Dosis: X cm3/ha' para que pueda calcular costos."""
                    
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    st.session_state['rep'] = informe
                    
                    # CÁLCULO DE COSTO (Lógica simple de búsqueda)
                    costo_total = 0
                    detalles_costo = ""
                    for prod, precio in PRECIOS.items():
                        if prod.lower() in informe.lower():
                            # Buscamos un número cerca de la dosis (simplificado)
                            dosis_match = re.search(rf"{prod}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                            dosis = float(dosis_match.group(1).replace(',', '.')) if dosis_match else 1.0
                            # Si es cm3, lo pasamos a litros para el precio
                            if "cm3" in informe.lower(): dosis = dosis / 1000 if dosis > 10 else dosis
                            
                            costo_item = dosis * precio
                            costo_total += costo_item
                            detalles_costo += f"• {prod}: USD {costo_item:.2f}/ha\n"

                    st.markdown(f"""
                        <div class="reporte-box">
                            <h3 style="color: #1b5e20;">📋 INFORME Y PRESUPUESTO</h3>
                            <p style="color: black !important;">{informe.replace(chr(10), '<br>')}</p>
                            <hr style="border: 1px solid #eee">
                            <h4 style="color: #c0392b;">💰 INVERSIÓN ESTIMADA:</h4>
                            <p style="color: black !important; font-size: 18px;">{detalles_costo}<br><b>TOTAL: USD {costo_total:.2f} por Hectárea</b></p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state['costo'] = f"TOTAL ESTIMADO: USD {costo_total:.2f}/ha"
                    break
                except Exception as e:
                    continue

# 4. BOTÓN WHATSAPP
if 'rep' in st.session_state:
    costo_wa = st.session_state.get('costo', '')
    texto_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n📍 {cultivo} ({estado})\n\n{st.session_state['rep']}\n\n💵 *{costo_wa}*")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' class='btn-wa'>📲 MANDAR INFORME Y COSTOS</a>", unsafe_allow_html=True)
