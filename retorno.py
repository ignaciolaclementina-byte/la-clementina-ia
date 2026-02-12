import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración básica
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")
st.title("🚛 RETORNO MATCH")

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu Excel
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # LEER: No le ponemos nombre de pestaña, que traiga la primera que vea
        df = conn.read(spreadsheet=URL_DB, ttl="0")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            for index, row in df.iloc[::-1].iterrows():
                st.info(f"📍 **ORIGEN:** {row.get('origen', 'S/D')} | 📦 **ITEM:** {row.get('item', 'S/D')}\n\n💰 **PAGO:** {row.get('pago', 'S/D')} | 📞 **TEL:** {row.get('tel', 'S/D')}")
        else:
            st.warning("No se encontraron datos en el Excel.")
    except Exception as e:
        st.error(f"Error al leer: {e}")

with tab2:
    with st.form("form_viaje", clear_on_submit=True):
        st.subheader("Publicar nueva carga")
        f_origen = st.text_input("Origen")
        f_item = st.text_input("Item")
        f_pago = st.text_input("Pago")
        f_tel = st.text_input("Teléfono")
        
        if st.form_submit_button("PUBLICAR"):
            if f_origen and f_item:
                try:
                    df_actual = conn.read(spreadsheet=URL_DB, ttl="0")
                    nuevo = pd.DataFrame([{"origen": f_origen, "item": f_item, "pago": f_pago, "tel": f_tel}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final)
                    st.success("✅ ¡Publicado! Dale a Actualizar.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completá Origen e Item.")
