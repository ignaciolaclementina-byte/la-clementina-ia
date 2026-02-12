import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# 2. TÍTULO
st.title("🚛 RETORNO MATCH")
st.markdown("---")

# 3. CONEXIÓN A GOOGLE SHEETS
# Se conecta usando el bloque [gsheets] que pegaste en los Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu planilla (sin el #gid al final para máxima compatibilidad)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

# --- PESTAÑA 1: BUSCAR ---
with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Lee la hoja 'cargas'. IMPORTANTE: El nombre en el Excel debe ser 'cargas'
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas
            df.columns = df.columns.str.strip().str.lower()
            
            # Mostramos los viajes (del más nuevo al más viejo)
            for index, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.info(f"""
                    📍 **ORIGEN:** {row.get('ubicacion', 'S/D')}  
                    🎯 **DESTINO:** {row.get('destino', 'S/D')}  
                    🚛 **UNIDAD:** {row.get('unidad', 'S/D')}  
                    👤 **CONTACTO:** {row.get('nombre', 'S/D')}
                    """)
        else:
            st.warning("Todavía no hay viajes publicados en la hoja 'cargas'.")
            
    except Exception as e:
        st.error(f"⚠️ Error de conexión.")
        st.info(f"Detalle técnico: {e}")
        st.write("Asegurate de que la pestaña del Excel se llame **cargas** y que el mail de la cuenta de servicio tenga acceso de **Editor**.")

# --- PESTAÑA 2: PUBLICAR ---
with tab2:
    st.subheader("Publicá tu retorno aquí")
    with st.form("formulario_viaje", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre / Empresa")
        unidad = st.text_input("Tipo de Unidad (ej: Sider, Playo)")
        ubicacion = st.text_input("¿Dónde estás ahora? (Ciudad/Provincia)")
        destino = st.text_input("¿Hacia dónde vas?")
        
        submit = st.form_submit_button("PUBLICAR AHORA")
        
        if submit:
            if nombre and unidad and ubicacion and destino:
                try:
                    # Leemos datos actuales
                    df_existente = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
                    
                    # Creamos nueva fila
                    nuevo_viaje = pd.DataFrame([{
                        "nombre": nombre,
                        "unidad": unidad,
                        "ubicacion": ubicacion,
                        "destino": destino
                    }])
                    
                    # Unimos y subimos
                    df_actualizado = pd.concat([df_existente, nuevo_viaje], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, data=df_actualizado, worksheet="cargas")
                    
                    st.success("✅ ¡Publicado con éxito! Revisá la pestaña BUSCAR.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.warning("⚠️ Completá todos los campos.")

st.markdown("---")
st.caption("RETORNO MATCH - v1.1")
