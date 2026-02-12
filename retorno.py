import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE APARIENCIA PROFESIONAL
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    /* Fondo oscuro y moderno */
    .stApp {
        background: #0e1117;
    }
    
    /* Contenedor de las tarjetas */
    .card {
        background: #1d2129;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 15px;
        border-left: 6px solid #2ecc71;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    .card h3 { color: #2ecc71; margin-bottom: 5px; }
    .card p { color: #cfd8dc; margin: 3px 0; font-size: 1.1rem; }
    
    /* Botón de WhatsApp tipo App */
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: block;
        text-align: center;
        margin-top: 15px;
    }
    
    /* Pestañas estilizadas */
    .stTabs [data-baseweb="tab-list"] { background: #1d2129; padding: 5px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; }
    
    /* Ajuste del formulario para que no se vea tan "parche" */
    .form-container {
        background: white;
        border-radius: 20px;
        padding: 5px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# LINKS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

# INTERFAZ
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71;'>Logística inteligente San Jorge</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR CARGAS", "📤 PUBLICAR VIAJE"])

with tab1:
    if st.button("🔄 ACTUALIZAR"):
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
                <h3>📍 {str(r['origen']).upper()}</h3>
                <p><b>📦 CARGA:</b> {r['item']}</p>
                <p><b>💰 PAGO:</b> {r['pago']}</p>
                <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR POR WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando nuevos viajes en la zona...")

with tab2:
    st.markdown("<h3 style='color: white; text-align: center;'>Cargá tus datos aquí abajo</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    components.iframe(URL_FORM, height=700, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)
