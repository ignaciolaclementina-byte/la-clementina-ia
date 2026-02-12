import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

st.title("🚛 RETORNO MATCH")
st.markdown("---")

# 2. CONEXIÓN FORZANDO EL USO DE SECRETS
# Esto busca el bloque [connections.gsheets] en tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu Excel (limpia)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 3. INTERFAZ DE PESTAÑAS
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

# --- PESTAÑA: BUSCAR ---
with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Leemos la primera hoja disponible
        df = conn.read(spreadsheet=URL_DB, ttl="0")
        
        if df is not None and not df.empty:
            # Normalizamos nombres de columnas a minúsculas para evitar errores
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            # Mostramos los resultados en tarjetas (del más nuevo al más viejo)
            for index, row in df.iloc[::-1].iterrows():
                with st.container():
                    st.info(f"""
                    📍 **ORIGEN:** {row.get('origen', 'S/D')}  
                    📦 **ITEM:** {row.get('item', 'S/D')}  
                    💰 **PAGO:** {row.get('pago', 'S/D')}  
                    📞 **TEL:** {row.get('tel', 'S/D')}
                    """)
        else:
            st.warning("No hay viajes cargados aún.")
            
    except Exception as e:
        st.error("⚠️ Error al conectar con la base de datos.")
        st.info("Asegurate de que el mail de la Service Account sea EDITOR en el Excel.")

# --- PESTAÑA: PUBLICAR ---
with tab2:
    st.subheader("Cargá los datos de tu carga/camión")
    with st.form("form_viaje", clear_on_submit=True):
        f_origen = st.text_input("Origen (Ciudad/Provincia)")
        f_item = st.text_input("¿Qué cargás? (Ej: Sider, Chapa, Pallets)")
        f_pago = st.text_input("Pago / Tarifa")
        f_tel = st.text_input("Teléfono de contacto")
        
        btn_publicar = st.form_submit_button("PUBLICAR AHORA")
        
        if btn_publicar:
            if f_origen and f_item and f_tel:
                try:
                    # Traemos lo que ya existe
                    df_actual = conn.read(spreadsheet=URL_DB, ttl="0")
                    
                    # Creamos la nueva fila
                    nueva_fila = pd.DataFrame([{
                        "origen": f_origen,
                        "item": f_item,
                        "pago": f_pago,
                        "tel": f_tel
                    }])
                    
                    # Unimos y subimos al Excel usando la conexión segura
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=df_final)
                    
                    st.success("✅ ¡Publicado con éxito! Revisá la pestaña BUSCAR.")
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
                    st.info("Si el error dice 'Public Spreadsheet cannot be written to', es porque falta dar permiso de EDITOR al mail de la Service Account en el botón Compartir del Excel.")
            else:
                st.warning("Por favor, completá Origen, Item y Teléfono.")

st.markdown("---")
st.caption("RETORNO MATCH v1.3 - Logística colaborativa")
