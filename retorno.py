import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN VISUAL
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 8px solid #2ecc71; color: black; }
    .card-camion { border-left: 8px solid #3498db; }
    .card h3 { margin: 0; color: #1a1a1a; font-size: 1.3rem; }
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN (Lectura del Excel)
# Usamos tu link de publicación CSV para leer los datos
URL_DATOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# 3. INTERFAZ
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab_buscar, tab_publicar = st.tabs(["🔍 BUSCAR CARGAS/CAMIONES", "📝 PUBLICAR AHORA"])

# --- PESTAÑA BUSCAR ---
with tab_buscar:
    st.markdown("<h3 style='color:white'>Últimos Movimientos</h3>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR LISTA"):
        st.cache_data.clear()
        st.rerun()
        
    try:
        df = pd.read_csv(URL_DATOS)
        df.columns = df.columns.str.strip().str.lower()
        
        # Filtramos filas vacías
        df = df.dropna(subset=[df.columns[0]]) 
        
        for _, r in df.iterrows():
            # Detectamos si es camión o carga (ajustá esto según tus columnas reales)
            # Asumimos columna 0: Origen, 1: Detalle, 2: Pago, 3: Tel
            origen = str(r.iloc[0]).upper()
            detalle = str(r.iloc[1])
            pago = str(r.iloc[2])
            tel = str(r.iloc[3]).split('.')[0].replace(" ", "")
            
            # Icono y color según el contenido
            es_camion = "CAMION" in detalle.upper() or "VACIO" in detalle.upper()
            clase = "card-camion" if es_camion else "card"
            icon = "🚛" if es_camion else "📦"
            
            st.markdown(f"""
            <div class="{clase}">
                <h3>{icon} {origen}</h3>
                <p><b>Detalle:</b> {detalle}</p>
                <p><b>Valor:</b> {pago}</p>
                <a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none; color:#25D366; font-weight:bold; display:block; margin-top:10px;">
                    📲 CONTACTAR AHORA
                </a>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.info("Conectando con la base de datos...")

# --- PESTAÑA PUBLICAR (Aquí está el truco) ---
with tab_publicar:
    st.markdown("<div style='background: white; padding: 20px; border-radius: 15px;'>", unsafe_allow_html=True)
    st.subheader("Cargá tus datos aquí 👇")
    
    # PEGA ACÁ TU LINK DE GOOGLE FORMS
    # Ejemplo: "https://docs.google.com/forms/d/e/1FAIpQLSe.../viewform?embedded=true"
    # Asegurate de que termine en 'viewform?embedded=true' para que se vea bien
    LINK_FORMULARIO = "PEGAR_AQUI_TU_LINK_DEL_FORMULARIO" 
    
    if "PEGAR_AQUI" in LINK_FORMULARIO:
        st.warning("⚠️ Faltan configurar el link del Formulario en el código.")
        st.info("Pasos: Creá un Google Form -> Vinculalo a tu Excel -> Copiá el link -> Pegalo en el código.")
    else:
        # Esto incrusta el formulario DENTRO de la app. El usuario no sale nunca.
        components.iframe(LINK_FORMULARIO, height=800, scrolling=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
