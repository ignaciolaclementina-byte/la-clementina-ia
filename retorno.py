import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# Título visual
st.title("🚛 RETORNO MATCH")
st.markdown("---")

# 2. CONEXIÓN A GOOGLE SHEETS
# Busca el bloque [connections.gsheets] en tus Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error de configuración en los Secrets.")
    st.stop()

# URL de tu base de datos (Excel)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 3. INTERFAZ DE PESTAÑAS
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

# --- PESTAÑA 1: BUSCAR ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("Viajes Disponibles")
    with col2:
        if st.button("🔄 ACTUALIZAR"):
            st.cache_data.clear()
            st.rerun()

    try:
        # Leemos la primera hoja del Excel (ttl=0 para que no use caché vieja)
        df = conn.read(spreadsheet=URL_DB, ttl="0")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas (sacar espacios y pasar a minúsculas)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Mostramos los viajes del más nuevo al más viejo
            for index, row in df.iloc[::-1].iterrows():
                with st.expander(f"📍 {row.get('origen', 'S/D')} ➡️ {row.get('item', 'Carga')}", expanded=True):
                    st.write(f"💰 **Pago:** {row.get('pago', 'A convenir')}")
                    st.write(f"📞 **Contacto:** {row.get('tel', 'S/D')}")
        else:
            st.info("Todavía no hay viajes publicados. ¡Sé el primero!")
            
    except Exception as e:
        st.error("No se pudo leer la base de datos.")
        st.info("Asegurate de que el mail de la Service Account sea 'Editor' en tu Excel.")

# --- PESTAÑA 2: PUBLICAR ---
with tab2:
    st.subheader("Publicá tu carga o camión")
    
    with st.form("form_viaje", clear_on_submit=True):
        f_origen = st.text_input("📍 Origen (¿De dónde sale?)")
        f_item = st.text_input("📦 Item (¿Qué se carga o qué camión es?)")
        f_pago = st.text_input("💰 Pago / Tarifa aproximada")
        f_tel = st.text_input("📞 Teléfono de contacto")
        
        enviar = st.form_submit_button("PUBLICAR AHORA")
        
        if enviar:
            if f_origen and f_item and f_tel:
                try:
                    # Traemos los datos actuales
                    df_actual = conn.read(spreadsheet=URL_DB, ttl="0")
                    
                    # Creamos la nueva fila (los nombres de columnas deben coincidir con el Excel)
                    nueva_fila = pd.DataFrame([{
                        "origen": f_origen,
                        "item": f_item,
                        "pago": f_pago,
                        "tel": f_tel
                    }])
                    
                    # Unimos y subimos
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final)
                    
                    st.success("✅ ¡Publicado con éxito! Andá a la pestaña BUSCAR para verlo.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Por favor, completá los campos obligatorios: Origen, Item y Teléfono.")

# Pie de página
st.markdown("---")
st.caption("RETORNO MATCH - Sistema de Logística Colaborativa")
