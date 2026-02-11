import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. LLAVE (Tu API Key está perfecta)
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Lista de precios para el cálculo
PRECIOS = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .card { background-color: white; padding: 20px; border-radius: 10px; color: black; border-left: 10px solid #1b5e20; }
    h1, label { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; font-weight: bold; height: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. INTERFAZ
col1, col2 = st.columns(2)
with col1:
    cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2:
    has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

archivo = st.file_uploader("Subir foto del lote", type=["jpg", "png", "jpeg"])

if archivo:
    img = Image.open(archivo).convert('RGB')
    st.image(img, caption="Imagen cargada")
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("Conectando con el Ingeniero IA..."):
            try:
                # AQUÍ ESTÁ LA SOLUCIÓN AL 404: Conexión limpia sin 'v1beta'
                genai.configure(api_key=API_KEY)
                # Forzamos el uso del modelo estable
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                vademecum = ", ".join(PRECIOS.keys())
                prompt = f"Analiza esta imagen de {cultivo}. Identifica plagas/malezas y receta solo productos de esta lista: {vademecum}. Formato: 'Producto: Dosis'."
                
                # Pedir respuesta
                respuesta = model.generate_content([prompt, img])
                informe = respuesta.text
                
                # Mostrar Reporte
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.subheader("📋 REPORTE AGRONÓMICO")
                st.write(informe)
                
                # Cálculo de inversión estimado (simplificado para evitar fallos)
                costo_estimado = 0.0
                for p, precio in PRECIOS.items():
                    if p.lower() in informe.lower():
                        costo_estimado += (precio * 0.5 * has)
                
                st.markdown(f"### 💰 Inversión estimada: USD {costo_estimado:.2f}")
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Preparar mensaje de WhatsApp
                msg_wa = urllib.parse.quote(f"🚜 *LA CLEMENTINA IA*\n🌱 {cultivo} ({has} ha)\n\n{informe}\n\n💰 Total: USD {costo_estimado:.2f}")
                st.markdown(f'<a href="https://wa.me/543406649346?text={msg_wa}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; margin-top:10px;">📲 ENVIAR POR WHATSAPP</button></a>', unsafe_allow_html=True)

            except Exception as e:
                # Corregimos el error de la línea 93 del intento anterior
                st.error(f"Error de conexión: {str(e)}")
