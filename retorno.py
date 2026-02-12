import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")
st.title("🚛 RETORNO MATCH")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()
    try:
        # Lee la pestaña 'cargas' que ya existe en tu Excel
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            for index, row in df.iloc[::-1].iterrows():
                # Mostramos los datos según tus columnas actuales: origen, item, pago, tel
                st.info(f"📍 **ORIGEN:** {row.get('origen', '-')} | 📦 **ITEM:** {row.get('item', '-')}\n\n💰 **PAGO:** {row.get('pago', '-')} | 📞 **TEL:** {row.get('tel', '-')}")
        else:
            st.warning("No hay datos en la pestaña 'cargas'.")
    except Exception as e:
        st.error(f"Error: {e}")

with tab2:
    with st.form("form_viaje", clear_on_submit=True):
        st.subheader("Publicar nueva carga")
        f_origen = st.text_input("Origen")
        f_item = st.text_input("Item (Qué se carga)")
        f_pago = st.text_input("Pago aproximado")
        f_tel = st.text_input("Teléfono de contacto")
        
        if st.form_submit_button("PUBLICAR"):
            if f_origen and f_item:
                try:
                    df_actual = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    nuevo = pd.DataFrame([{"origen": f_origen, "item": f_item, "pago": f_pago, "tel": f_tel}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                    st.success("✅ ¡Publicado con éxito!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completá al menos Origen e Item.")
