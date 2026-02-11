import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN DE SEGURIDAD Y API
# Tu clave actual ya está integrada aquí
CLAVE_API = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Lista de precios para el cálculo automático
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = ", ".join(PRECIOS.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DE LA INTERFAZ
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.6); }
    .card { background-color: white; padding: 20px; border-radius: 15px; color: black !important; border-left: 8px solid #1b5e20; }
    h1, label, p { color: white !important; font-weight: bold !important; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
col1, col2, col3 = st.columns(3)
with col1: cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2: estado = st.text_input("ESTADO", "R3")
with col3: hectareas = st.number_input("HAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Subir imagen de la hoja", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, caption="Imagen cargada", use_container_width=True)
    
    if st.button("🚀 ANALIZAR AHORA"):
        with st.spinner("El Ingeniero IA está revisando el lote..."):
            try:
                # CONFIGURACIÓN SIN ERRORES 404
                genai.configure(api_key=CLAVE_API)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Instrucción para la IA
                prompt = f"Sos un experto agrónomo. Analizá esta foto de {cultivo} en estado {estado}. Identificá plagas o enfermedades. Recetá productos de esta lista: {VADEMECUM}. Especificá 'Dosis: X l/ha' para cada uno."
                
                respuesta = model.generate_content([prompt, img])
                texto_informe = respuesta.text
                
                # Cálculo de costos y dosis
                costo_total = 0.0
                detalle_compra = []
                
                for producto, precio in PRECIOS.items():
                    if producto.lower() in texto_informe.lower():
                        match = re.search(rf"{producto}.*?(\d+[.,]?\d*)", texto_informe, re.IGNORECASE)
                        if match:
                            dosis = float(match.group(1).replace(',', '.'))
                            if dosis > 10: dosis /= 1000 # Ajuste de cm3 a lts
                            costo_total += (dosis * precio * hectareas)
                            detalle_compra.append(f"• {producto}: {dosis * hectareas:.1f} lts totales")

                # Mostrar Resultados
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='color:#1b5e20;'>📋 REPORTE TÉCNICO: {cultivo.upper()}</h3>", unsafe_allow_html=True)
                st.write(texto_informe)
                st.markdown("---")
                if detalle_compra:
                    st.markdown("**INSUMOS NECESARIOS:**")
                    for item in detalle_compra: st.write(item)
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>TOTAL: USD {costo_total:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Guardar para WhatsApp
                st.session_state['reporte_wa'] = f"🚜 *INFORME LA CLEMENTINA*\n🌱 Cultivo: {cultivo}\n📍 Lote: {hectareas} ha\n\n{texto_informe}\n\n💰 *Inversión Total: USD {costo_total:.2f}*"
                
            except Exception as e:
                st.error(f"Hubo un problema
