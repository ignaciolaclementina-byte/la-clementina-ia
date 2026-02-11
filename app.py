import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN (Tu API Key actual está perfecta)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Lista de precios para el cálculo automático
PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
PRODUCTOS_LISTA = ", ".join(PRECIOS_USD.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO VISUAL
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .card-informe { background-color: white; padding: 20px; border-radius: 10px; color: black !important; border-left: 8px solid #1b5e20; }
    h1, label, p, span { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; border-radius: 10px; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img_pil = Image.open(foto).convert('RGB')
    st.image(img_pil, use_container_width=True)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # AQUÍ SE ARREGLA EL 404: Conexión directa estable
                genai.configure(api_key=API_KEY)
                modelo_ia = genai.GenerativeModel('gemini-1.5-flash')
                
                # Instrucción (Prompt)
                prompt_agronomo = (
                    f"Actúa como agrónomo. Analiza la foto de {cul} en {est}. "
                    f"Identifica plagas y receta productos de: {PRODUCTOS_LISTA}. "
                    f"Usa el formato: 'Producto: Dosis l/ha'."
                )
                
                # Generar respuesta (Arreglado el error de corchetes)
                resultado = modelo_ia.generate_content([prompt_agronomo, img_pil])
                texto_informe = resultado.text
                
                # Lógica de costos e insumos
                total_usd_ha = 0.0
                compra_necesaria = []
                for p, precio in PRECIOS_USD.items():
                    if p.lower() in texto_informe.lower():
                        match = re.search(rf"{p}.*?(\d+[.,]?\d*)", texto_informe, re.IGNORECASE)
                        if match:
                            dosis = float(match.group(1).replace(',', '.'))
                            if dosis > 10: dosis /= 1000 # Convierte cm3 a litros
                            total_usd_ha += (dosis * precio)
                            compra_necesaria.append(f"• {p}: {dosis * has:.1f} lts")

                # MOSTRAR RESULTADOS
                st.markdown("<div class='card-informe'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#1b5e20;'>📋 REPORTE TÉCNICO</h3>", unsafe_allow_html=True)
                st.write(f"<p style='color:black;'>{texto_informe}</p>", unsafe_allow_html=True)
                
                if compra_necesaria:
                    st.markdown("<hr style='border-top: 1px solid #ccc;'>")
                    st.markdown("<b style='color:black;'>RESUMEN DE COMPRA:</b>", unsafe_allow_html=True)
                    for item in compra_necesaria:
                        st.write(f"<p style='color:black;'>{item}</p>", unsafe_allow_html=True)
                    
                    inversion_total = total_usd_ha * has
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>TOTAL: USD {inversion_total:.2f}</h2>", unsafe_allow_html=True)
                    st.session_state['resumen_wa'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cul} ({has} ha)\n\n{texto_informe}\n\n💰 *Total: USD {inversion_total:.2f}*"
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                # AQUÍ SE ARREGLA EL ERROR DE LA LÍNEA 93
                st.error(f"Error técnico: {e}")

# 4. BOTÓN WHATSAPP
if 'resumen_wa' in st.session_state:
    mensaje_final = urllib.parse.quote(st.session_state['resumen_wa'])
    link_wa = f"https://wa.me/543406649346?text={mensaje_final}"
    st.markdown(f"""
        <a href="{link_wa}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:15px; border: 2px solid white;">
                📲 ENVIAR REPORTE A WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
