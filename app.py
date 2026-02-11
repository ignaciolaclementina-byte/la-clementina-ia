import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse
import re

# 1. CONFIGURACIÓN DE SEGURIDAD Y PRECIOS
CLAVE_API = "AIzaSyAk1b1J69Nvsmzbbr5BZyW8UZlVpAtOgmo"
PRECIOS_USD = {
    "Round Up": 9.0, "2,4-D": 11.5, "Cripton": 48.0, 
    "Ampligo": 52.0, "Solomon": 40.0, "Optimizer": 6.5, 
    "Rizo Spray": 5.0, "YaraVita": 14.0
}
LISTA_PRODUCTOS = ", ".join(PRECIOS_USD.keys())

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO DE LA INTERFAZ (ESTILO CAMPO)
st.markdown("""
    <style>
    .stApp { 
        background: url("https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=1920&auto=format&fit=crop") no-repeat center center fixed; 
        background-size: cover; 
    }
    [data-testid="stAppViewContainer"] { background-color: rgba(0, 0, 0, 0.5); }
    .informe-card { 
        background-color: white; 
        padding: 20px; 
        border-radius: 10px; 
        color: black !important; 
        border-left: 8px solid #1b5e20;
    }
    h1, h2, h3, label, p, span { color: white !important; font-weight: bold; }
    .stButton>button { width: 100%; background: #1b5e20 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚜 LA CLEMENTINA IA</h1>", unsafe_allow_html=True)

# 3. ENTRADA DE DATOS DEL LOTE
col1, col2, col3 = st.columns(3)
with col1: cultivo = st.selectbox("CULTIVO", ["Soja", "Maíz", "Trigo", "Alfalfa", "Barbecho"])
with col2: estado = st.text_input("ESTADO", "R3")
with col3: hectareas = st.number_input("HECTÁREAS", min_value=1.0, value=100.0)

# El sistema de carga que ya dominás
foto = st.camera_input("") or st.file_uploader("Subir imagen del lote", type=["jpg", "png", "jpeg"])

if foto:
    imagen_pil = Image.open(foto).convert('RGB')
    st.image(imagen_pil, caption="Imagen cargada correctamente", use_container_width=True)
    
    if st.button("🚀 INICIAR ANÁLISIS"):
        with st.spinner("El Ingeniero IA está analizando la muestra..."):
            try:
                # CONEXIÓN CORREGIDA (SOLUCIÓN AL ERROR 404)
                genai.configure(api_key=CLAVE_API)
                # Usamos la dirección estable del modelo
                modelo = genai.GenerativeModel('gemini-1.5-flash')
                
                instruccion = (
                    f"Actúa como un agrónomo experto. Analiza la foto de {cultivo} en estado {estado}. "
                    f"Detecta plagas o enfermedades. Receta productos de esta lista únicamente: {LISTA_PRODUCTOS}. "
                    f"Formato obligatorio: 'Producto: Dosis l/ha'."
                )
                
                # Respuesta de la IA
                respuesta = modelo.generate_content([instruccion, imagen_pil])
                texto_informe = respuesta.text
                
                # Lógica de costos (Cálculo automático)
                costo_por_ha = 0.0
                detalle_compra = []
                for prod, precio in PRECIOS_USD.items():
                    if prod.lower() in texto_informe.lower():
                        busqueda = re.search(rf"{prod}.*?(\d+[.,]?\d*)", texto_informe, re.IGNORECASE)
                        if busqueda:
                            dosis = float(busqueda.group(1).replace(',', '.'))
                            if dosis > 10: dosis = dosis / 1000 # Maneja cm3 a litros
                            costo_por_ha += (dosis * precio)
                            detalle_compra.append(f"• {prod}: {dosis * hectareas:.1f} lts")

                # MOSTRAR RESULTADOS EN PANTALLA
                st.markdown("<div class='informe-card'>", unsafe_allow_html=True)
                st.markdown("<h3 style='color:#1b5e20;'>📋 INFORME DE DIAGNÓSTICO</h3>", unsafe_allow_html=True)
                st.write(f"<span style='color:black;'>{texto_informe}</span>", unsafe_allow_html=True)
                
                if detalle_compra:
                    st.markdown("<hr style='border-top: 1px solid #ccc;'>")
                    st.markdown("<b style='color:black;'>LOGÍSTICA DE COMPRA RECOMENDADA:</b>", unsafe_allow_html=True)
                    for item in detalle_compra:
                        st.write(f"<span style='color:black;'>{item}</span>", unsafe_allow_html=True)
                    
                    total_final = costo_por_ha * hectareas
                    st.markdown(f"<h2 style='text-align:right; color:#1b5e20;'>INVERSIÓN: USD {total_final:.2f}</h2>", unsafe_allow_html=True)
                    
                    # Guardar para WhatsApp
                    st.session_state['resumen'] = f"🚜 *LA CLEMENTINA IA*\n🌱 {cultivo} ({hectareas} ha)\n\n{texto_informe}\n\n💰 *Total: USD {total_final:.2f}*"
                st.markdown("</div>", unsafe_allow_html=True)
                
            except Exception as error:
                st.error(f"Error en la conexión: {error}. Verificá tu conexión a internet.")

# 4. ENVÍO A WHATSAPP
if 'resumen' in st.session_state:
    texto_wa = urllib.parse.quote(st.session_state['resumen'])
    link = f"https://wa.me/543406649346?text={texto_wa}"
    st.markdown(f"""
        <a href="{link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; margin-top:15px; border: 2px solid white;">
                📲 ENVIAR REPORTE POR WHATSAPP
            </div>
        </a>
    """, unsafe_allow_html=True)
