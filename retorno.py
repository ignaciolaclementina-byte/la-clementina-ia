import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de la App
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# 2. Conexión a la base de datos (Google Sheets)
# Esto usa automáticamente el bloque [gsheets] que pegaste en Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. URL de tu planilla (Verificada)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

st.title("🚛 RETORNO MATCH")

# Creamos las pestañas
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Intentamos leer la hoja llamada "cargas"
        # IMPORTANTE: Tu hoja de Excel abajo DEBE llamarse 'cargas'
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        
        if df is not None and not df.empty:
            # Limpiamos los nombres de las columnas por si tienen espacios
            df.columns = df.columns.str.strip().str.lower()
            
            # Mostramos los viajes del último al primero
            for _, r in df.iloc[::-1].iterrows():
                with st.container():
                    st.info(f"📍 {r.get('ubicacion', 'S/D')} -> {r.get('destino', 'S/D')} | 🚛 {r.get('unidad', 'S/D')} | 👤 {r.get('nombre', 'Anónimo')}")
        else:
            st.warning("No hay viajes registrados. ¡Sé el primero en publicar!")
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        st.info("💡 Consejo: Revisá que la pestaña de tu Excel se llame exactamente 'cargas'.")

with tab2:
    with st.form("form_registro"):
        st.write("### Completá los datos del viaje")
        f_nom = st.text_input("Nombre del transportista")
        f_uni = st.text_input("Tipo de Unidad (ej: Sider, Playo)")
        f_ubi = st.text_input("¿Dónde estás ahora?")
        f_des = st.text_input("¿Hacia dónde vas?")
        
        btn_publicar = st.form_submit_button("PUBLICAR RETORNO")
        
        if btn_publicar:
            if f_nom and f_uni and f_ubi and f_des:
                try:
                    # Leemos lo que ya hay
                    df_previo = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    # Creamos la nueva fila
                    nuevo_dato = pd.DataFrame([{
                        "nombre": f_nom, 
                        "unidad": f_uni, 
                        "ubicacion": f_ubi, 
                        "destino": f_des
                    }])
                    # Unimos y subimos
                    df_final = pd.concat([df_previo, nuevo_dato], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final, worksheet="cargas")
                    
                    st.success("✅ ¡Publicado con éxito! Actualizá la lista para verlo.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.warning("⚠️ Por favor, completá todos los campos.")
