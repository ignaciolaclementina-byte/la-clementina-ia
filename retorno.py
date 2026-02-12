import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# 2. ESTILO
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card-viaje { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black !important; border-left: 10px solid #2ecc71; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN (Usa el nombre [gsheets] de tus Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9lMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    try:
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iloc[::-1].iterrows():
                origen = r.get('origen', 'Sin especificar')
                item = r.get('item', '-')
                pago = r.get('pago', '-')
                tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
                st.markdown(f'<div class="card-viaje"><h3 style="color:black">📍 {str(origen).upper()}</h3><p style="color:black">📦 <b>Carga:</b> {item} | 💰 <b>Tarifa:</b> {pago}</p><a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR</a></div>', unsafe_allow_html=True)
        else:
            st.info("No hay viajes todavía.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

with tab2:
    with st.form("form_nuevo", clear_on_submit=True):
        origen = st.text_input("¿Desde dónde salís?")
        item = st.text_input("¿Qué llevás o buscás?")
        pago = st.text_input("Tarifa / Pago")
        tel = st.text_input("WhatsApp (Ej: 3406400000)")
        if st.form_submit_button("PUBLICAR AHORA"):
            if origen and tel:
                try:
                    current_df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    nuevo = pd.DataFrame([{"origen": origen, "item": item, "pago": pago, "tel": tel}])
                    updated_df = pd.concat([current_df, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=updated_df, worksheet="cargas")
                    st.success("¡Publicado!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
