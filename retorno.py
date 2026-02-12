import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")

st.title("🚛 RETORNO MATCH")

# 2. Conexión (usa los secretos que ya guardaste bien)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Tu URL de la planilla (Asegurate que sea esta exacto)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

tabs = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tabs[0]:
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Intentamos leer la planilla. 
        # Si da error 400, es porque el nombre de la hoja "cargas" no existe abajo
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
        
        if df is not None and not df.empty:
            for _, row in df.iloc[::-1].iterrows():
                st.info(f"📍 {row.get('ubicacion', 'S/D')} -> {row.get('destino', 'S/D')} | 🚛 {row.get('unidad', 'S/D')}")
        else:
            st.write("No hay viajes todavía.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Revisá que la hoja de tu Excel se llame exactamente 'cargas' (en minúsculas)")

with tabs[1]:
    with st.form("registro"):
        st.subheader("Publicar Retorno")
        nombre = st.text_input("Nombre")
        unidad = st.text_input("Unidad")
        origen = st.text_input("Ubicación actual")
        destino = st.text_input("Destino")
        
        if st.form_submit_button("PUBLICAR"):
            if nombre and unidad and origen and destino:
                try:
                    df_actual = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
                    nuevo = pd.DataFrame([{"nombre": nombre, "unidad": unidad, "ubicacion": origen, "destino": destino}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, data=df_final, worksheet="cargas")
                    st.success("¡Publicado!")
                except:
                    st.error("Error al guardar. Revisá los permisos de edición.")
