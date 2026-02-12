import streamlit as st
import pandas as pd

# 1. CONFIGURACION
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. CONEXION
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# 3. ASPECTO VISUAL (Fondo y Título)
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    h1, h2, h3, p, label, .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .info-box { background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2ecc71; }
    .info-box p, .info-box h3 { color: #2c3e50 !important; margin: 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. FUNCION CARGAR
def cargar(url):
    try:
        df = pd.read_csv(url).dropna(how='all')
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
            st.markdown(f"""
            <div class='info-box'>
                <h3>📍 {r['origen']}</h3>
                <p>📦 Carga: {r['item']} | 💰 ${r['pago']}</p>
                <p>📲 Tel: {r['tel']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay cargas vigentes en el Excel.")

with t2:
    st.write("Próximamente: Links a formularios.")

with t3:
    if not df_cam.empty:
        for _, r in df_cam.iterrows():
            st.write(f"🚛 {r['nombre']} - 📍 {r['origen']}")
    else:
        st.write("No hay camiones reportados.")
