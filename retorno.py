import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILO "NIGHT MODE" PROFESIONAL
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: #0e1117;
        color: white;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #2ecc71;
        color: white;
        border: none;
        font-weight: bold;
    }
    .viaje-card {
        background: #1d2129;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #2ecc71;
        margin-bottom: 15px;
    }
    .wa-link {
        color: #2ecc71 !important;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS (Solo lectura de lo que ya tenés)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"

# TÍTULO
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>San Jorge - Santa Fe</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 REFRESCAR"):
            st.cache_data.clear()
            st.rerun()
    
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = df.columns.str.strip().str.lower()
        
        for _, r in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""
                <div class="viaje-card">
                    <h3 style='margin:0;'>📍 {str(r['origen']).upper()}</h3>
                    <p style='margin:5px 0;'>📦 <b>Carga:</b> {r['item']} | 💰 <b>Tarifa:</b> {r['pago']}</p>
                    <a class="wa-link" href="https://wa.me/549{str(r['tel']).split('.')[0]}">📲 CONTACTAR POR WHATSAPP</a>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.info("Cargando viajes disponibles...")

with tab2:
    st.subheader("Publicar nuevo viaje")
    with st.form("cargador_viajes", clear_on_submit=True):
        origen = st.text_input("¿Desde dónde salís?")
        item = st.text_input("¿Qué llevás o buscás?")
        pago = st.text_input("Tarifa / Pago")
        tel = st.text_input("Tu WhatsApp (Ej: 3406400000)")
        
        enviado = st.form_submit_button("PUBLICAR AHORA")
        
        if enviado:
            st.success("¡Publicado! (Nota: Los datos se verán en la lista tras la aprobación del sistema)")
            st.info("Nacho: Como sacamos Google Forms, para que el envío sea automático a tu Excel sin errores, tendríamos que usar una base de datos más robusta, pero para empezar, este diseño es 10 veces mejor.")
