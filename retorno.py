import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# ESTILO MEJORADO
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .card-form {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    .card-viaje {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: black !important;
        border-left: 10px solid #2ecc71;
    }
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

t1, t2 = st.tabs(["🔍 BUSCAR CARGAS", "📤 PUBLICAR MI RETORNO"])

with t1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip().str.lower()
        df = df.dropna(subset=['origen'])
        for _, r in df.iloc[::-1].iterrows():
            tel = str(r['tel']).split('.')[0].replace(" ", "").replace("+", "")
            st.markdown(f"""
            <div class="card-viaje">
                <h3 style="color:black; margin:0;">📍 {str(r['origen']).upper()}</h3>
                <p style="color:black;">📦 <b>Carga:</b> {r['item']} | 💰 <b>Pago:</b> {r['pago']}</p>
                <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando viajes...")

with t2:
    st.markdown("<div class='card-form'>", unsafe_allow_html=True)
    # Reducimos el alto y lo centramos más
    components.iframe(URL_FORM, height=650, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)
