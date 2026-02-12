import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración básica
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")

st.title("🚛 RETORNO MATCH")
st.markdown("---")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# URL LIMPIA (sin el #gid=0 al final)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Intentamos leer la hoja 'cargas'
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            for index, row in df.iloc[::-1].iterrows():
                st.info(f"📍 **ORIGEN:** {row.get('ubicacion', 'S/D')} | 🎯 **DESTINO:** {row.get('destino', 'S/D')}\n\n🚛 **UNIDAD:** {row.get('unidad', 'S/D')} | 👤 **CONTACTO:** {row.get('nombre', 'S/D')}")
        else:
            st.warning("No hay datos en la pestaña 'cargas'.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("Revisá que la pestaña del Excel se llame exactamente 'cargas' (en minúsculas).")

with tab2:
    st.subheader("Publicá tu viaje")
    with st.form("form_viaje", clear_on_submit=True):
        nombre = st.text_input("Nombre / Empresa")
        unidad = st.text_input("Tipo de Unidad")
        ubicacion = st.text_input("¿Dónde estás?")
        destino = st.text_input("¿A dónde vas?")
        enviar = st.form_submit_button("PUBLICAR")
        
        if enviar:
            if nombre and unidad and ubicacion and destino:
                try:
                    df_actual = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    nuevo = pd.DataFrame([{"nombre": nombre, "unidad": unidad, "ubicacion": ubicacion, "destino": destino}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                    st.success("✅ ¡Publicado con éxito!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completá todos los campos.")
