import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. TUS DATOS (Mantenemos tus claves que ya funcionan)
CLAVES = ["AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw", "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"]
VADEMECUM = "ADHERENTES: Optimizer, Rizo Spray. BIOESTIMULANTES: YaraVita. FUNGICIDAS: Cripton. HERBICIDAS: Round Up, 2,4-D. INSECTICIDAS: Solomon, Ampligo."
MI_NUMERO = "543406649346"

# Diccionario de precios para el cálculo automático
PRECIOS_DOLARES = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO "PANTALLA NÍTIDA"
st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed;
        background-size: cover;
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.4); }
    .titulo { color: #ffffff; text-align: center; font-size: 40px; font-weight: 900; text-shadow: 2px 2px 5px #000000; margin-top: -30px; }
    .sub-txt { color: #ffffff !important; text-align: center; font-size: 18px; font-weight: bold; text-shadow: 1px 1px 3px #000000; }
    label, p, span, div.stMarkdown { color: #ffffff !important; font-weight: 800 !important; }
    .stButton>button { 
        width: 100%; border-radius: 12px; background-color: #2e7d32 !important; 
        color: white !important; height: 55px; font-size: 20px; border: 2px solid #ffffff;
    }
    .btn-wa { 
        display: block; background-color: #25D366; color: white !important; padding: 15px; 
        border-radius: 12px; text-decoration: none; text-align: center; font-weight: bold; border: 2px solid white; font-size: 18px; margin-top: 15px;
    }
    .reporte-box {
        background-color: white !important; padding: 25px; border-radius: 15px; 
        color: black !important; border-left: 10px solid #2e7d32; box-shadow: 0px 6px 20px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. INTERFAZ
st.markdown("<div class='titulo'>🚜 LA CLEMENTINA IA</div>", unsafe_allow_html=True)
st.markdown("<p class='sub-txt'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

# Entrada de hectáreas para el cálculo
has = st.number_input("CANTIDAD DE HECTÁREAS DEL LOTE:", min_value=1.0, value=100.0)

opcion = st.radio("ORIGEN DE LA IMAGEN:", ["📸 CÁMARA", "📁 GALERÍA"], horizontal=True)

if opcion == "📸 CÁMARA":
    foto = st.camera_input("")
else:
    foto = st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button('🚀 ANALIZAR Y CALCULAR INVERSIÓN'):
        with st.spinner('El Ingeniero IA está analizando el lote...'):
            for key in CLAVES:
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"""Sos un Ingeniero Agrónomo senior de San Jorge, Santa Fe. 
                    Analizá la imagen. Identificá malezas, plagas o deficiencias.
                    Recetá una solución usando ÚNICAMENTE estos productos: {VADEMECUM}.
                    IMPORTANTE: Para cada producto, especificá la DOSIS RECOMENDADA por hectárea (l/ha o cm3/ha).
                    Formato: 'Producto: Dosis'."""
                    
                    res = model.generate_content([prompt, img])
                    informe = res.text
                    
                    # --- Lógica de cálculo de dólares ---
                    costo_acumulado = 0.0
                    for prod, precio in PRECIOS_DOLARES.items():
                        if prod.lower() in informe.lower():
                            # Busca el número de la dosis cerca del nombre del producto
                            match = re.search(rf"{prod}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                            if match:
                                dosis = float(match.group(1).replace(',', '.'))
                                if dosis > 10: dosis /= 1000 # Convierte cm3 a litros
                                costo_acumulado += (dosis * precio * has)

                    # Guardar en sesión
                    st.session_state['rep'] = informe
                    st.session_state['total'] = costo_acumulado
                    
                    # Mostrar Reporte
                    st.markdown(f"""
                        <div class='reporte-box'>
                            <b style='color: #2e7d32; font-size: 20px;'>📋 REPORTE TÉCNICO:</b><br><br>
                            <div style='color: black;'>{informe.replace(chr(10), '<br>')}</div>
                            <hr style='border: 1px solid #eee;'>
                            <h2 style='color: #2e7d32; text-align: right;'>INVERSIÓN TOTAL: USD {costo_acumulado:.2f}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    break
                except:
                    continue

# 4. BOTÓN WHATSAPP
if 'rep' in st.session_state:
    texto_wa = urllib.parse.quote(
        f"🚜 *REPORTE LA CLEMENTINA IA*\n"
        f"🌱 Lote de {has} hectáreas\n\n"
        f"{st.session_state['rep']}\n\n"
        f"💰 *INVERSIÓN TOTAL: USD {st.session_state['total']:.2f}*"
    )
    st.markdown(f"<a href='https://wa.me/{MI_NUMERO}?text={texto_wa}' target='_blank' class='btn-wa'>📲 ENVIAR REPORTE AL WHATSAPP</a>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; font-size: 11px; color: white;'>Desarrollado por Ignacio Diaz</p>", unsafe_allow_html=True)
