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
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN (URL de tu imagen 4fd41c)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()
    try:
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iloc[::-1].iterrows():
                st.markdown(f"""
                <div class="card-viaje">
                    <h3 style="color:black">📍 {str(r.get('ubicacion','-')).upper()} -> {str(r.get('destino','-')).upper()}</h3>
                    <p style="color:black">🚛 <b>Unidad:</b> {r.get('unidad','-')} | 👤 <b>Ref:</b> {r.get('nombre','-')}</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    with st.form("form_nuevo", clear_on_submit=True):
        nom = st.text_input("Nombre")
        uni = st.text_input("Unidad")
        ubi = st.text_input("Ubicación")
        des = st.text_input("Destino")
        if st.form_submit_button("PUBLICAR"):
            if nom and ubi:
                try:
                    current_df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    nuevo = pd.DataFrame([{"nombre": nom, "unidad": uni, "ubicacion": ubi, "destino": des}])
                    updated_df = pd.concat([current_df, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=updated_df, worksheet="cargas")
                    st.success("¡Publicado!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
