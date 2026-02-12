import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 12px solid #2ecc71; }
    .card h3, .card p { color: #1a1a1a !important; }
    .stButton>button { width: 100%; background-color: #2ecc71; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN (Solo lectura para mostrar lo que ya se cargó)
URL_CARGAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# 3. INTERFAZ
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔍 VER DISPONIBLES", "📦 PUBLICAR CARGA", "🚛 PUBLICAR CAMIÓN"])

with tab1:
    st.subheader("Últimas publicaciones")
    try:
        df = pd.read_csv(URL_CARGAS)
        for _, r in df.dropna(subset=[df.columns[0]]).iterrows():
            st.markdown(f"""
            <div class='card'>
                <h3>📍 {str(r.iloc[0]).upper()}</h3>
                <p><b>Detalle:</b> {r.iloc[1]}</p>
                <p><b>Contacto:</b> {r.iloc[2]}</p>
                <a href="https://wa.me/549{r.iloc[2]}" style="text-decoration:none; color:#25D366; font-weight:bold;">📲 CONTACTAR AHORA</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("No hay publicaciones recientes.")

with tab2:
    st.subheader("📤 Datos de la Carga")
    # Formulario embebido de Google (La forma más segura de cargar datos sin fallos)
    # Deberías crear un Google Form y pegar el link acá:
    st.markdown("""
        <iframe src="TU_LINK_DE_GOOGLE_FORM_AQUÍ?embedded=true" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
    """, unsafe_allow_html=True)

with tab3:
    st.subheader("🚛 Datos del Camión")
    st.markdown("""
        <iframe src="TU_LINK_DE_GOOGLE_FORM_AQUÍ?embedded=true" width="100%" height="600" frameborder="0" marginheight="0" marginwidth="0">Cargando…</iframe>
    """, unsafe_allow_html=True)
