import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# DISEÑO DE ALTO NIVEL (CSS)
st.markdown("""
    <style>
    /* Fondo con imagen de camión de alta calidad */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075");
        background-size: cover;
    }
    
    /* Tarjetas de los viajes */
    .card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        color: #1e1e1e;
        border-left: 12px solid #2ecc71;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    
    /* Títulos dentro de la tarjeta */
    .card h3 { margin-top: 0; color: #2c3e50; font-size: 1.6rem; }
    
    /* Botón de WhatsApp estilizado */
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        transition: 0.3s;
    }
    .btn-ws:hover { background-color: #128C7E; transform: scale(1.05); }
    
    /* Tabs (Pestañas) */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px 10px 0 0;
        color: white !important;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# LINKS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

# TÍTULO PRINCIPAL
st.markdown("<h1 style='text-align: center; color: #2ecc71; font-size: 3rem; text-shadow: 2px 2px 4px #000;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: white; font-size: 1.2rem;'>Conectando cargas y camiones en tiempo real</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES DISPONIBLES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    st.write("---")
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🔄 REFRESCAR LISTADO", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip().str.lower()
        df = df.dropna(subset=['origen'])
        
        for _, r in df.iloc[::-1].iterrows():
            tel = str(r['tel']).split('.')[0].replace(" ", "").replace("+", "")
            st.markdown(f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>📍 {str(r['origen']).upper()}</h3>
                    <span style="color: gray; font-size: 0.8rem;">ACTIVO ✅</span>
                </div>
                <hr>
                <p style="font-size: 1.1rem;">📦 <b>¿Qué lleva?:</b> {r['item']}</p>
                <p style="font-size: 1.1rem;">💰 <b>Tarifa/Pago:</b> <span style="color: #27ae60; font-weight: bold;">{r['pago']}</span></p>
                <div style="text-align: right;">
                    <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR AHORA</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown("<div style='text-align: center; color: white; padding: 50px;'><h3>Aún no hay cargas. ¡Sé el primero en publicar!</h3></div>", unsafe_allow_html=True)

with tab2:
    st.markdown("""
        <div style='background: white; border-radius: 20px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);'>
            <h2 style='color: #2c3e50; text-align: center;'>Completá los datos del viaje</h2>
            <p style='color: #7f8c8d; text-align: center;'>Tu publicación aparecerá al instante en la lista de búsqueda.</p>
    """, unsafe_allow_html=True)
    components.iframe(URL_FORM, height=800, scrolling=True
