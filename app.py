import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
from datetime import datetime
import re

# 1. LISTA DE PRECIOS (Editá los valores en USD según tu agronomía)
PRECIOS = {
    "Round Up": 9.0, 
    "2,4-D": 11.5, 
    "Cripton": 48.0, 
    "Ampligo": 52.0, 
    "Solomon": 40.0, 
    "Optimizer": 6.5, 
    "Rizo Spray": 5.0, 
    "YaraVita": 14.0
}

CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO AGRO-MODERNO
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
    .reporte-box { background-color: white; padding: 25px; border-radius: 15px; border-left: 12px solid #1b5e20; color: black !important; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); }
    </style>
    """, unsafe_allow_html=True)

# 3. CUERPO DE LA APP
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-txt'>San Jorge • Gestión de Insumos</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    cultivo = st.selectbox("CULTIVO:", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2:
    estado = st.text_input("ESTADO (Ej: V4, R2):", "V-Indefinido")

foto = st.camera_input("") or st.file_uploader("Subir imagen", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR Y COTIZAR AHORA'):
        with st.spinner('Analizando cultivo y calculando costos...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""Sos un Agrónomo senior. Analizá esta foto de {cultivo} en {estado}.
                    1. Da diagnóstico técnico.
                    2. Recetá productos de: {VADEMECUM}.
                    3. IMPORTANTE: Para cada producto poné la dosis exacta como 'Dosis: X l/ha' o 'Dosis: X cm3/ha'."""
                    
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    
                    # Lógica de Costos
                    costo_total = 0.0
                    items_costo = []
                    
                    for prod, precio in PRECIOS.items():
                        if prod.lower() in informe.lower():
                            # Busca el número más cercano a la palabra del producto
                            regex = rf"{prod}.*?(\d+[.,]?\d*)"
                            match = re.search(regex, informe, re.IGNORECASE)
                            if match:
                                dosis = float(match.group(1).replace(',', '.'))
                                # Ajuste si la dosis es en cm3 (pasa a lts para el cálculo)
                                if dosis > 10: dosis = dosis / 1000
                                subtotal = dosis * precio
                                costo_total += subtotal
                                items_costo.append(f"• {prod}: {dosis:.3f} l/ha -> **USD {subtotal:.2f}**")

                    st.markdown(f"""
                        <div class="reporte-box">
                            <h3 style="color: #1b5e20; margin-top:0;">📋 INFORME TÉCNICO</h3>
                            <p style="color: #333 !important;">{informe.replace(chr(10), '<br>')}</p>
                            <hr>
                            <h4 style="color: #c0392b;">💰 PRESUPUESTO ESTIMADO (USD/ha)</h4>
                            <p style="color: #333 !important;">{"<br>".join(items_costo)}</p>
                            <h3 style="color: #1b5e20; text-align:right;">TOTAL: USD {costo_total:.2f}/ha</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state['rep'] = informe
                    st.session_state['costo'] = f"TOTAL ESTIMADO: USD {costo_total:.2f}/ha"
                    break
                except:
                    continue

if 'rep' in st.session_state:
    txt_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n📍 {cultivo} ({estado})\n\n{st.session_state['rep']}\n\n💵 *{st.session_state['costo']}*")
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={txt_wa}' target='_blank' class='btn-wa'>📲 ENVIAR REPORTE COMPLETO</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; opacity:0.6; color:white;'>Ignacio Diaz - Gestión Agronómica</p>", unsafe_allow_html=True)
