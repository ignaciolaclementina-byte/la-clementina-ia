import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la App
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛")
st.title("🚛 RETORNO MATCH")

# 2. Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# URL Limpia (aseguramos que no tenga basura al final)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Intentamos leer la pestaña 'cargas'
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas", ttl="0")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas (pasa todo a minúscula y saca espacios)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            for index, row in df.iloc[::-1].iterrows():
                # Usamos .get para que si falta una columna no se rompa la app
                st.info(f"📍 **ORIGEN:** {row.get('origen', 'S/D')} | 📦 **ITEM:** {row.get('item', 'S/D')}\n\n💰 **PAGO:** {row.get('pago', 'S/D')} | 📞 **TEL:** {row.get('tel', 'S/D')}")
        else:
            st.warning("La pestaña 'cargas' está vacía.")
            
    except Exception as e:
        st.error("⚠️ Error al conectar con Google Sheets.")
        st.write(f"Detalle: {e}")
        st.info("Verificá que la pestaña del Excel se llame exactamente 'cargas' y que la primera fila tenga títulos.")

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
                    st.success("✅ ¡Publicado! Dale a Actualizar en la otra pestaña.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.warning("Completá Origen e Item.")
