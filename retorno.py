import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")
st.title("🚛 RETORNO MATCH")

# Conexión usando el bloque [gsheets] de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL Limpia de tu Excel
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Intentamos leer. Si 'cargas' falla, trae la primera hoja disponible.
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas", ttl="0")
        
        if df is not None and not df.empty:
            # Normalizamos nombres de columnas a minúsculas
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            for index, row in df.iloc[::-1].iterrows():
                st.info(f"📍 **ORIGEN:** {row.get('origen', 'S/D')} | 📦 **ITEM:** {row.get('item', 'S/D')}\n\n💰 **PAGO:** {row.get('pago', 'S/D')} | 📞 **TEL:** {row.get('tel', 'S/D')}")
        else:
            st.warning("No se encontraron datos. Asegurate de que la primera fila del Excel tenga títulos.")
            
    except Exception as e:
        st.error("⚠️ Error de comunicación con Google.")
        st.info("Intentá renombrar la pestaña de tu Excel a 'cargas' (todo minúscula) y que el mail de la cuenta de servicio sea EDITOR.")

with tab2:
    st.subheader("Publicar nueva carga")
    with st.form("form_viaje", clear_on_submit=True):
        f_origen = st.text_input("Origen")
        f_item = st.text_input("Item")
        f_pago = st.text_input("Pago")
        f_tel = st.text_input("Teléfono")
        
        if st.form_submit_button("PUBLICAR"):
            if f_origen and f_item:
                try:
                    df_actual = conn.read(spreadsheet=URL_DB, worksheet="cargas", ttl="0")
                    nuevo = pd.DataFrame([{"origen": f_origen, "item": f_item, "pago": f_pago, "tel": f_tel}])
                    df_final = pd.concat([df_actual, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                    st.success("✅ ¡Publicado! Revisá la pestaña BUSCAR.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.warning("Por favor, completá Origen e Item.")
