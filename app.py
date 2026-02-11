import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. CONFIGURACIÓN ÚNICA
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Diccionario de precios
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO LIMPIO
st.markdown("""
    <style>
    .stApp { background: #0e1117; }
    .reporte { background-color: white; padding: 20px; border-radius: 10px; color: black; border-left: 10px solid #1b5e20; }
    h1, label { color: white !important; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. INTERFAZ DE USUARIO
col1, col2 = st.columns(2)
with col1:
    cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2:
    hectareas = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.camera_input("Captura o subí foto del lote") or st.file_uploader("O seleccioná un archivo", type=["jpg", "png", "jpeg"])

if foto:
    imagen = Image.open(foto).convert('RGB')
    st.image(imagen, caption="Imagen cargada")
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Analizando con IA..."):
            try:
                # CONFIGURACIÓN SIN 'v1beta' (Elimina el Error 404)
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                vademecum = ", ".join(PRECIOS.keys())
                prompt = f"Sos ingeniero agrónomo. Analiza este {cultivo}. Recetá productos de: {vademecum}. Formato: 'Producto: Dosis l/ha'."
                
                # Ejecución de la IA
                respuesta = model.generate_content([prompt, imagen])
                texto = respuesta.text
                
                # Mostrar resultados
                st.markdown("<div class='reporte'>", unsafe_allow_html=True)
                st.subheader("📋 REPORTE DEL LOTE")
                st.write(texto)
                
                # Cálculo rápido de inversión
                costo_total = 0.0
                for prod, precio in PRECIOS.items():
                    if prod.lower() in texto.lower():
                        costo_total += (precio * 0.5 * hectareas) # Estimación base
                
                st.markdown(f"### 💰 Inversión estimada: USD {costo_total:.2f}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Link de WhatsApp
                msg = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n🌱 {cultivo}: {hectareas} ha\n\n{texto}\n\n💰 Total: USD {costo_total:.2f}")
                st.markdown(f'<a href="https://wa.me/543406649346?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; margin-top:10px;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error técnico: {str(e)}")
