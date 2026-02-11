import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. LLAVE Y PRECIOS (Tu API Key está OK)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
VADEMECUM = ", ".join(PRECIOS_USD.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DE LA APP
st.markdown("""
    <style>
    .stApp { background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; background-size: cover; }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .card { background-color: white; padding: 20px; border-radius: 10px; color: black !important; border-left: 8px solid #1b5e20; }
    h1, label, p, span { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS
c1, c2, c3 = st.columns(3)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: est = st.text_input("ESTADO", "R3")
with c3: has = st.number_input("HAS", min_value=1.0, value=100.0)

foto = st.camera_input("") or st.file_uploader("Subir foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, use_container_width=True)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("El Ingeniero IA está analizando..."):
            try:
                # SOLUCIÓN AL 404: Conexión directa
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Como agrónomo experto, analiza esta foto de {cul} en {est}. Diagnostica problemas y receta solo: {VADEMECUM}. Usa el formato 'Producto: Dosis l/ha'."
                
                # Generar respuesta (Corregido el error de corchetes y comillas)
                res = model.generate_content([prompt, img])
                informe = res.text
                
                # Cálculo de costos e insumos
                costo_ha = 0.0
                compra = []
                for p, precio in PRECIOS_USD.items():
                    if p.lower() in informe.lower():
                        match = re.search(rf"{p}.*?(\d+[.,]?\d*)", informe, re.IGNORECASE)
                        if match:
                            d = float(match.group(1).replace(',', '.'))
                            if d > 10: d /= 1000 # Convierte cm3 a lts
                            costo_ha += (d * precio)
                            compra.append(f"• {p}: {d*has:.1f} lts totales")

                # MOSTRAR RESULTADOS
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#1b5e20;'>📋 REPORTE TÉCNICO</h3>", unsafe_allow_html=True)
                st.write(f"<p style='color:black;'>{informe}</p>", unsafe_allow_html=True)
                
                if compra:
                    st.markdown("<hr>")
                    st.markdown("<b style='color:black;'>INSUMOS NECESARIOS:</b>", unsafe_allow_html=True)
                    for item in compra:
                        st.write(f"<p style='color:black;'>{item}</p>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>INVERSIÓN: USD {costo_ha * has:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                st.session_state['msg_wa'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cul} ({has} ha)\n\n{informe}\n\n💰 *Total: USD {costo_ha * has:.2f}*"

            except Exception as e:
                # Cierre de bloque corregido (except obligatorio)
                st.error(f"Error de conexión: {e}")

# 4. BOTÓN WHATSAPP
if 'msg_wa' in st.session_state:
    texto = urllib.parse.quote(st.session_state['msg_wa'])
    st.markdown(f"""
        <a href="https://wa.me/543406649346?text={texto}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text
