import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# 2. TÍTULO Y ESTILO
st.title("🚛 RETORNO MATCH")
st.markdown("---")

# 3. CONEXIÓN A GOOGLE SHEETS
# El nombre "gsheets" debe coincidir con el bloque [gsheets] de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu planilla (sin el #gid al final para evitar errores 400)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 4. CREACIÓN DE PESTAÑAS
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

# --- PESTAÑA 1: BUSCAR VIAJES ---
with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()

    try:
        # Lee la hoja llamada 'cargas'
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas (por si hay espacios o mayúsculas)
            df.columns = df.columns.str.strip().str.lower()
            
            # Invertimos el orden para ver lo más nuevo arriba
            for index, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.info(f"""
                    **📍 ORIGEN:** {row.get('ubicacion', 'S/D')}  
                    **🎯 DESTINO:** {row.get('destino', 'S/D')}  
                    **🚛 UNIDAD:** {row.get('unidad', 'S/D')}  
                    **👤 CONTACTO:** {row.get('nombre', 'S/D')}
                    """)
        else:
            st.warning("Todavía no hay viajes publicados en la hoja 'cargas'.")
            
    except Exception as e:
        st.error("⚠️ Error de conexión con la base de datos.")
        st.info("Revisá que la pestaña del Excel se llame exactamente 'cargas' y que el mail de la cuenta de servicio sea Editor.")

# --- PESTAÑA 2: PUBLICAR RETORNO ---
with tab2:
    st.subheader("Cargá tus datos aquí")
    with st.form("formulario_viaje", clear_on_submit=True):
        nombre = st.text_input("Tu Nombre / Empresa")
        unidad = st.text_input("Tipo de Unidad (Sider, Playo, Chasis, etc.)")
        ubicacion = st.text_input("¿Dónde estás ahora? (Ciudad/Provincia)")
        destino = st.text_input("¿A dónde vas?")
        
        submit = st.form_submit_button("PUBLICAR AHORA")
        
        if submit:
            if nombre and unidad and ubicacion and destino:
                try:
                    # Traemos los datos actuales
                    df_existente = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
                    
                    # Creamos la nueva fila
                    nuevo_viaje = pd.DataFrame([{
                        "nombre": nombre,
                        "unidad": unidad,
                        "ubicacion": ubicacion,
                        "destino": destino
                    }])
                    
                    # Concatenamos y actualizamos
                    df_actualizado = pd.concat([df_existente, nuevo_viaje], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, data=df_actualizado, worksheet="cargas")
                    
                    st.success("✅ ¡Viaje publicado con éxito! Volvé a la pestaña BUSCAR para verlo.")
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")
            else:
                st.warning("Por favor, completá todos los campos del formulario.")

# 5. PIE DE PÁGINA
st.markdown("---")
st.caption("RETORNO MATCH v1.0 - Sistema de logística colaborativa.")
