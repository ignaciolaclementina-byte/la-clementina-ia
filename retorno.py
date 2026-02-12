import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# ESTILO
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 8px solid #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

# CONEXIÓN
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

st.title("🚛 RETORNO MATCH")

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
                <div class="card">
                    <h3 style="color:black">📍 {str(r.get('ubicacion','-')).upper()} -> {str(r.get('destino','-')).upper()}</h3>
                    <p style="color:black">🚛 <b>Unidad:</b> {r.get('unidad','-')} | 👤 <b>Ref:</b> {r.get('nombre','-')}</p>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    with st.form("nuevo"):
        nom = st.text_input("Nombre")
        uni = st.text_input("Unidad")
        ubi = st.text_input("Ubicación")
        des = st.text_input("Destino")
        if st.form_submit_button("PUBLICAR"):
            try:
                df_actual = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                nuevo = pd.DataFrame([{"nombre": nom, "unidad": uni, "ubicacion": ubi, "destino": des}])
                df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                st.success("¡Listos!")
            except Exception as e:
                st.error(f"Error: {e}")
