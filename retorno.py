import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

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
        # worksheet="cargas" debe coincidir con tu Excel
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            # Corregido el error de sintaxis del iloc
            for _, r in df.iloc[::-1].iterrows():
                st.info(f"📍 {r.get('ubicacion','-')} -> {r.get('destino','-')} | 🚛 {r.get('unidad','-')} | 👤 {r.get('nombre','-')}")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

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
                st.success("¡Publicado!")
            except Exception as e:
                st.error(f"Error: {e}")
