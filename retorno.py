import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH")

# 2. LINK CORREGIDO (ID verificado de tu captura)
# Aseguramos que el ID sea el exacto de tu barra de direcciones
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=0"

st.title("🚛 RETORNO MATCH")

# 3. FUNCIÓN DE CARGA
def cargar_datos():
    try:
        # Leemos el Excel directamente
        df = pd.read_csv(URL)
        # Limpiamos los nombres de las columnas
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Botón para refrescar
if st.button("🔄 ACTUALIZAR DATOS"):
    st.cache_data.clear()

df = cargar_datos()

# 4. MOSTRAR RESULTADOS
if df is not None:
    if not df.empty:
        st.success("✅ ¡Conectado con éxito!")
        # Recorremos las filas que tengan un origen
        for _, r in df.dropna(subset=['origen']).iterrows():
            with st.expander(f"📍 ORIGEN: {str(r['origen']).upper()}", expanded=True):
                st.write(f"📦 **Carga:** {r.get('item', '-')}")
                st.write(f"💰 **Pago:** ${r.get('pago', '-')}")
                st.write(f"📲 **Tel:** {r.get('tel', '-')}")
                
                # Botón de WhatsApp
                tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
                if tel:
                    st.markdown(f'[📲 CONTACTAR POR WHATSAPP](https://wa.me/549{tel})')
    else:
        st.warning("El Excel parece no tener datos debajo de los títulos.")
