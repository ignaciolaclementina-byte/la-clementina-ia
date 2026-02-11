import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. CREDENCIALES
API_KEY = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"

# Diccionario de productos y precios base
PRODUCTOS_INFO = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. ESTILO VISUAL MODO OSCURO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 15px; color: #1a1a1a !important; border-left: 10px solid #2e7d32; }
    h1, label { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #2e7d32 !important; color: white !important; border-radius: 10px; height: 50px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. INTERFAZ DE USUARIO
c1, c2 = st.columns(2)
with c1:
    cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with c2:
    has = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

foto = st.file_uploader("Subir foto del lote", type=["jpg", "png", "jpeg"])

if foto:
    img_obj = Image.open(foto).convert('RGB')
    st.image(img_obj, caption="Imagen para procesar")
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("El Ingeniero IA está analizando la imagen..."):
            try:
                # SOLUCIÓN AL 404: Configuración sin 'v1beta'
                genai.configure(api_key=API_KEY)
                
                # Usamos el modelo estable de Gemini 1.5 Flash
                model_engine = genai.GenerativeModel('gemini-1.5-flash')
                
                lista_prod = ", ".join(PRODUCTOS_INFO.keys())
                instruccion = (
                    f"Sos experto en agro. Analiza este {cultivo}. "
                    f"Si ves plagas o malezas, receta productos de esta lista: {lista_prod}. "
                    f"Usa el formato: 'Producto: Dosis'."
                )
                
                # Ejecutar análisis
                response = model_engine.generate_content([instruccion, img_obj])
                texto_final = response.text
                
                # Mostrar el reporte en pantalla
                st.markdown("<div class='report-card'>", unsafe_allow_html=True)
                st.subheader("📋 REPORTE DE CAMPO")
                st.write(texto_final)
                
                # Cálculo de inversión (Lógica protegida)
                inversion = 0.0
                for p, precio in PRODUCTOS_INFO.items():
                    if p.lower() in texto_final.lower():
                        inversion += (precio * 0.5 * has) # Estimación estándar
                
                st.markdown(f"<h2 style='text-align:right; color:#2e7d32;'>COSTO ESTIMADO: USD {inversion:.2f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Guardar datos para WhatsApp
                st.session_state['resumen'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cultivo} ({has} ha)\n\n{texto_final}\n\n💰 *Total: USD {inversion:.2f}*"

            except Exception as error:
                # Arreglado el error de las comillas en el mensaje de error
                st.error(f"Aviso: {str(error)}")

# 4. BOTÓN WHATSAPP
if 'resumen' in st.session_state:
    texto_wa = urllib.parse.quote(st.session_state['resumen'])
    link = f"https://wa.me/543406649346?text={texto_wa}"
    st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:12px; text-align:center; font-weight:bold; margin-top:20px; border: 1px solid white;">
                📲 ENVIAR REPORTE POR WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
