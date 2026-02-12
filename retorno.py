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
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            # Iteramos mostrando los datos
            for index, row in df.iterrows():
                st.info(f"📍 {row.get('ubicacion', '-')} -> {row.get('destino', '-')} | 🚛 {row.get('unidad', '-')} | 👤 {row.get('nombre', '-')}")
    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    with st.form("nuevo"):
        st.write("Publicar Carga:")
        nombre = st.text_input("Nombre")
        unidad = st.text_input("Unidad")
        ubicacion = st.text_input("Ubicación")
        destino = st.text_input("Destino")
        if st.form_submit_button("PUBLICAR"):
            try:
                df_actual = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                nuevo = pd.DataFrame([{"nombre": nombre, "unidad": unidad, "ubicacion": ubicacion, "destino": destino}])
                df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                st.success("¡Publicado!")
            except Exception as e:
                st.error(f"Error: {e}")
