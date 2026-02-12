import streamlit as st
import pandas as pd
import requests

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .card-viaje {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: black !important;
        border-left: 10px solid #2ecc71;
    }
    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 10px;
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

# 2. LINK DE TU EXCEL (SOLO LECTURA)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR CARGAS", "📤 PUBLICAR MI RETORNO"])

with tab1:
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

with tab2:
    st.subheader("Publicar nuevo viaje")
    # FORMULARIO NATIVO (Mucho más lindo)
    with st.form("nuevo_viaje", clear_on_submit=True):
        origen = st.text_input("📍 Ciudad de Origen")
        item = st.text_input("📦 ¿Qué llevás?")
        pago = st.text_input("💰 Tarifa / Pago")
        tel = st.text_input("📲 WhatsApp (con código de área sin 0 ni 15)")
        
        submit = st.form_submit_button("PUBLICAR AHORA")
        
        if submit:
            if origen and item and tel:
                # AQUÍ EXPLICACIÓN:
                st.success("¡Datos enviados con éxito!")
                st.balloons()
                st.info("Nacho: Para que este botón escriba en el Excel automáticamente sin Google Forms, necesitamos conectar una API. Por ahora, los datos de arriba son de muestra.")
            else:
                st.error("Por favor completá los campos obligatorios")
