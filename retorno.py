import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Título de la app
st.title("🚛 RETORNO MATCH")

# Crea la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

# URL de tu planilla
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit#gid=0"

try:
    # Lee los datos de la hoja "cargas"
    df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
    
    if df is not None:
        st.success("✅ ¡Conectado a la base de datos!")
        st.write("### Viajes Disponibles")
        st.dataframe(df)
    else:
        st.warning("La planilla está vacía.")

except Exception as e:
    st.error(f"Error al leer los datos: {e}")
    st.info("Revisá que la pestaña del Excel se llame 'cargas' y que hayas compartido el Excel con el mail de vendedor@...")
