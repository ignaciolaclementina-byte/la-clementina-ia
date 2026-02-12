import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACION DE PAGINA
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. CONEXION (Tu ID de Excel)
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# 3. DISEÑO PRO (El aspecto que te gustaba)
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #2ecc71; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .card h3, .card p, .card b { color: #2c3e50 !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. FUNCION CARGAR DATOS
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
            <div class='card'>
                <h3>📍 {r['origen']}</h3>
                <p>📦 <b>Carga:</b> {r['item']}</p>
                <p>💰 <b>Pago:</b> ${r['p
