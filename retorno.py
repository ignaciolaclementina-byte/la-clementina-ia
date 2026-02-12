import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la App
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

st.title("🚛 RETORNO MATCH")
st.markdown("---")

# 2. Conexión (usa los secretos [gsheets] que ya guardaste)
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. URL de tu planilla (Limpiada para evitar Error 400)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 4. Pestañas
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Intentamos leer la hoja 'cargas'
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
        
        if df is not None and not df.empty:
            # Normalizamos nombres de columnas para que no fallen
            df.columns = df.columns.str.strip().str.lower()
            
            # Mostramos los viajes del último al primero
            for index, row in df.iloc[::-1].iterrows():
                st.info(f"📍 **ORIGEN:** {row.get('ubicacion', 'S/D')} | 🎯 **DESTINO:** {row.get('destino', 'S/D')}\n\n🚛 **UNIDAD:** {row.get('unidad', 'S/D')} | 👤 **CONTACTO:** {row.get('nombre', 'S/D')}")
        else:
            st.warning("Todavía no hay viajes publicados en la hoja 'cargas'.")
            
    except Exception as e:
        st.error(f"⚠️ Error de conexión")
        st.info("Revisá que la pestaña del Excel se llame exactamente 'cargas' (en minúsculas) y que la primera fila tenga los títulos: nombre, unidad, ubicacion, destino.")

with tab2:
    st.subheader("Publicá tu viaje")
    with st.form("form_viaje", clear_on_submit=True):
        f_nom = st.text_input("Nombre / Empresa")
        f_uni = st.text_input("Tipo de Unidad")
        f_ubi = st.text_input("¿Dónde estás ahora?")
        f_des = st.text_input("¿Hacia dónde vas?")
        
        if st.form_submit_button("PUBLICAR"):
            if f_nom and f_uni and f_ubi and f_des:
                try:
                    # Leemos datos actuales
                    df_previo = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
                    # Creamos nueva fila
                    nuevo = pd.DataFrame([{"nombre": f_nom, "unidad": f_uni, "ubicacion": f_ubi, "destino": f_des}])
                    # Unimos y subimos
                    df_final = pd.concat([df_previo, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, data=df_final, worksheet="cargas")
                    st.success("✅ ¡Publicado con éxito!")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completá todos los campos.")
