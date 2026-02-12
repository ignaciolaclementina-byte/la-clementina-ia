import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card-viaje { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black !important; border-left: 10px solid #2ecc71; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN (URL corregida con 'I' mayúscula)
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    try:
        # Leemos la pestaña 'cargas'
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
        if df is not None and not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iloc[::-1].iterrows():
                # Ajustado a tus columnas: nombre, unidad, ubicacion, destino
                nombre = r.get('nombre', 'Sin nombre')
                unidad = r.get('unidad', '-')
                ubi = r.get('ubicacion', '-')
                dest = r.get('destino', '-')
                
                st.markdown(f"""
                <div class="card-viaje">
                    <h3 style="color:black">📍 {str(ubi).upper()} -> {str(dest).upper()}</h3>
                    <p style="color:black">👤 <b>Contacto:</b> {nombre} | 🚛 <b>Unidad:</b> {unidad}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hay datos en la pestaña 'cargas'.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

with tab2:
    with st.form("form_nuevo", clear_on_submit=True):
        st.markdown("<p style='color:white'>Completá los datos para publicar:</p>", unsafe_allow_html=True)
        nombre = st.text_input("Nombre / Empresa")
        unidad = st.text_input("Tipo de Unidad")
        ubicacion = st.text_input("Ubicación actual")
        destino = st.text_input("Destino deseado")
        
        if st.form_submit_button("PUBLICAR AHORA"):
            if nombre and ubicacion:
                try:
                    current_df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                    nuevo = pd.DataFrame([{"nombre": nombre, "unidad": unidad, "ubicacion": ubicacion, "destino": destino}])
                    updated_df = pd.concat([current_df, nuevo], ignore_index=True)
                    conn.update(spreadsheet=URL_DB, data=updated_df, worksheet="cargas")
                    st.success("¡Publicado!")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completá nombre y ubicación.")
