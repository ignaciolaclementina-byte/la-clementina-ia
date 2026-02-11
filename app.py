import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVE Y MODELO (Sin v1beta para evitar el Error 404)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Listado de precios para cálculo rápido
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO VISUAL
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .informe-card { background-color: white; padding: 20px; border-radius: 12px; color: black !important; border-left: 10px solid #1b5e20; }
    h1, label { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. INTERFAZ
c1, c2 = st.columns(2)
with c1: cul = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2: has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.file_uploader("Cargar imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    img = Image.open(foto).convert('RGB')
    st.image(img, caption="Imagen para análisis")
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # CONFIGURACIÓN DIRECTA (Solución al 404)
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                vademecum = ", ".join(PRECIOS.keys())
                prompt = f"Actúa como agrónomo. Analiza este {cul}. Identifica problemas y receta productos de: {vademecum}. Formato: 'Producto: Dosis'."
                
                # Respuesta de la IA
                res = model.generate_content([prompt, img])
                informe_texto = res.text
                
                # Cálculo de inversión estimado
                total_usd = 0.0
                for p, precio in PRECIOS.items():
                    if p.lower() in informe_texto.lower():
                        total_usd += (precio * 0.5 * has) # Cálculo base estimado

                # MOSTRAR RESULTADOS
                st.markdown("<div class='informe-card'>", unsafe_allow_html=True)
                st.subheader("📋 REPORTE AGRONÓMICO")
                st.write(f"<div style='color:black;'>{informe_texto}</div>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>TOTAL: USD {total_usd:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Guardar para WhatsApp
                st.session_state['msg'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cul} ({has} ha)\n\n{informe_texto}\n\n💰 *Inversión: USD {total_usd:.2f}*"

            except Exception as e:
                st.error(f"Error de conexión: {str(e)}. Reintentá en un momento.")

# 4. BOTÓN WHATSAPP
if 'msg' in st.session_state:
    link = f"https://wa.me/543406649346?text={urllib.parse.quote(st.session_state['msg'])}"
    st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:15px;">
                📲 ENVIAR INFORME A WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
