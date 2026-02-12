import streamlit as st
import pandas as pd

# 1. CONFIGURACION
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. CONEXION (Tu ID de Excel)
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# 3. TITULO
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. CARGAR DATOS
def cargar(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

df_ca = cargar(URL_CARGAS)
df_cam = cargar(URL_CAMIONES)

# 5. PESTAÑAS
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 CAMIONES"])

with t1:
    if not df_ca.empty:
        for _, r in df_ca.iterrows():
            with st.container():
                st.markdown(f"### 📍 {r['origen']}")
                st.write(f"📦 Carga: {r['item']} | 💰 Pago: ${r['pago']}")
                st.write(f"📲 WhatsApp: {r['tel']}")
                st.divider()
    else:
        st.warning("No hay datos en 'cargas'. Revisá el Excel.")

with t2:
    st.write("Sección para publicar (Formularios)")

with t3:
    if not df_cam.empty:
        for _, r in df_cam.iterrows():
            st.write(f"🚛 {r['nombre']} - 📍 {r['origen']}")
    else:
        st.write("No hay camiones en la lista.")

# 6. ESTILO DE FONDO (Simple)
st.markdown("<style>.stApp { background: #2c3e50; }</style>", unsafe_allow_html=True)
