import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# 2. DISEÑO CON EL FONDO QUE TE GUSTABA
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: black !important;
        border-left: 10px solid #2ecc71;
    }
    .card h3, .card p { color: black !important; margin: 5px 0; }
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }
    .stTabs [data-baseweb="tab"] { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LINKS (Excel y Formulario)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

# 4. TÍTULO
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR CARGAS", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Leemos el Excel
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip().str.lower()
        # Filtramos filas vacías
        df = df.dropna(subset=['origen'])
        
        # Mostramos de más nuevo a más viejo
        for _, r in df.iloc[::-1].iterrows():
            # Limpiamos el número de teléfono
            tel_base = str(r['tel']).split('.')[0].replace(" ", "").replace("+", "")
            
            st.markdown(f"""
            <div class="card">
                <h3>📍 ORIGEN: {str(r['origen']).upper()}</h3>
                <p>📦 <b>Detalle:</b> {r['item']}</p>
                <p>💰 <b>Pago:</b> {r['pago']}</p>
                <a class="btn-ws" href="https://wa.me/549{tel_base}" target="_blank">📲 CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Conectando con el listado de cargas...")

with tab2:
    st.markdown("<div style='background: white; border-radius: 15px; padding: 10px;'>", unsafe_allow_html=True)
    components.iframe(URL_FORM, height=800, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)
