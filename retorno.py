import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="RETORNO MATCH")

# 2. CONEXIÓN AL EXCEL (ID verificado)
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=0"

# 3. TITULO SIMPLE
st.title("🚛 RETORNO MATCH")

# 4. CARGA DE DATOS
try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty:
        st.success("✅ ¡Conectado al Excel!")
        # Mostramos los viajes en tarjetas simples
        for _, r in df.dropna(subset=['origen']).iterrows():
            with st.container():
                st.subheader(f"📍 {r['origen']}")
                st.write(f"📦 Carga: {r.get('item', '-')}")
                st.write(f"💰 Pago: ${r.get('pago', '-')}")
                st.write(f"📲 Tel: {r.get('tel', '-')}")
                st.divider()
    else:
        st.warning("El Excel está vacío.")
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 5. BOTÓN PARA REFRESCAR MANUALMENTE
if st.button("🔄 ACTUALIZAR DATOS"):
    st.cache_data.clear()
