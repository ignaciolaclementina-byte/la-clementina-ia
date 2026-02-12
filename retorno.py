import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# Estilo personalizado para que se vea más profesional
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    </style>
    """, unsafe_allow_value=True)

# 2. TÍTULO
st.title("🚛 RETORNO MATCH")
st.subheader("Conectando transporte en tiempo real")
st.markdown("---")

# 3. CONEXIÓN A GOOGLE SHEETS
# Se conecta usando el bloque [gsheets] de tus Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu planilla (limpia, sin parámetros extra)
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

# --- PESTAÑA 1: BUSCAR ---
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("### Listado de Retornos Disponibles")
    with col2:
        if st.button("🔄 ACTUALIZAR"):
            st.cache_data.clear()
            st.rerun()

    try:
        # Lee la hoja 'cargas'. IMPORTANTE: El nombre en el Excel debe ser 'cargas'
        df = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
        
        if df is not None and not df.empty:
            # Limpiamos nombres de columnas por seguridad
            df.columns = df.columns.str.strip().str.lower()
            
            # Mostramos los viajes (del más nuevo al más viejo)
            for index, row in df.iloc[::-1].iterrows():
                with st.expander(f"🚛 {row.get('ubicacion', 'S/D')} ➡ {row.get('destino', 'S/D')}", expanded=True):
                    st.write(f"**👤 Transportista:** {row.get('nombre', 'S/D')}")
                    st.write(f"**📦 Unidad:** {row.get('unidad', 'S/D')}")
                    st.write(f"**📍 Ubicación:** {row.get('ubicacion', 'S/D')}")
                    st.write(f"**🎯 Destino:** {row.get('destino', 'S/D')}")
        else:
            st.warning("Aún no hay viajes publicados. ¡Sé el primero!")
            
    except Exception as e:
        st.error(f"⚠️ Error de conexión.")
        st.info("Revisá que la pestaña del Excel se llame exactamente 'cargas' y que el mail del service account tenga acceso de Editor.")

# --- PESTAÑA 2: PUBLICAR ---
with tab2:
    st.write("### Cargá los datos de tu camión")
    with st.form("formulario_viaje", clear_on_submit=True):
        nombre = st.text_input("Nombre o Empresa")
        unidad = st.text_input("Tipo de Unidad (Sider, Playo, Térmico...)")
        ubicacion = st.text_input("¿Dónde estás ahora? (Ciudad/Provincia)")
        destino = st.text_input("¿A qué zona vas?")
        
        submit = st.form_submit_button("PUBLICAR RETORNO")
        
        if submit:
            if nombre and unidad and ubicacion and destino:
                try:
                    # Traer datos actuales para no borrar lo viejo
                    df_actual = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas")
                    
                    # Crear nueva fila
                    nuevo_registro = pd.DataFrame([{
                        "nombre": nombre,
                        "unidad": unidad,
                        "ubicacion": ubicacion,
                        "destino": destino
                    }])
                    
                    # Sumar al listado y subir
                    df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True)
                    conn.update(spreadsheet=URL_PLANILLA, data=df_final, worksheet="cargas")
                    
                    st.success("✅ ¡Viaje publicado! Ya aparece en la lista de búsqueda.")
                except Exception as e:
                    st.error(f"Error al guardar datos: {e}")
            else:
                st.warning("⚠️ Por favor, completá todos los campos.")

st.markdown("---")
st.caption("RETORNO MATCH - v1.2")
