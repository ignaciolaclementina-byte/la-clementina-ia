import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN ---
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 8px solid #2ecc71; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .card b, .card p, .card h3 { color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
def cargar(url):
    try:
        d = pd.read_csv(url).dropna(how='all')
        d.columns = d.columns.str.strip().str.lower()
        return d
    except:
        return pd.DataFrame()

df_cargas = cargar(URL_CARGAS)
df_camiones = cargar(URL_CAMIONES)

t1, t2, t3 = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR", "🚛 CAMIONES DISPONIBLES"])

# --- TAB 1: BUSCAR CARGA ---
with t1:
    if not df_cargas.empty:
        opciones = ["Todos"] + sorted(df_cargas['origen'].unique().tolist())
        f = st.selectbox("¿Desde dónde buscás?", opciones)
        for _, r in df_cargas.iterrows():
            if f == "Todos" or str(r['origen']) == f:
                st.markdown(f"<div class='card'><h3>📍 {r['origen']}</h3><p>📦 {r['item']} | 💰 ${r['pago']}</p></div>", unsafe_allow_html=True)
                tel = str(r['tel']).split('.')[0]
                link = f"https://wa.me/549{tel}?text=Hola!+Vi+tu+carga+en+la+App"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:8px; font-weight:bold; margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    else:
        st.warning("No hay cargas vigentes en la planilla.")

# --- TAB 2: PUBLICAR ---
with t2:
    st.markdown("### 📤 Publicar Carga")
    with st.form("pub"):
        o = st.text_input("Origen")
        i = st.text_input("Mercadería")
        p = st.text_input("Pago")
        if st.form_submit_button("GENERAR WHATSAPP"):
            txt = urllib.parse.quote(f"NUEVA CARGA:\n📍 Origen: {o}\n📦 Item: {i}\n💰 Pago: {p}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={txt}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</div></a>', unsafe_allow_html=True)

# --- TAB 3: CAMIONES DISPONIBLES ---
with t3:
    st.markdown("### 🚛 Camiones buscando retorno")
    if not df_camiones.empty:
        for _, r in df_camiones.iterrows():
            st.markdown(f"""
            <div class='card'>
                <h3>🚛 {r['nombre']}</h3>
                <p>📍 Volviendo de: <b>{r['origen']}</b></p>
            </div>
            """, unsafe_allow_html=True)
            tel = str(r['tel']).split('.')[0]
            link = f"https://wa.me/549{tel}?text=Hola!+Vi+que+estas+en+{r['origen']}+buscando+retorno"
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background:#3498db; color:white; text-align:center; padding:10px; border-radius:8px; font-weight:bold; margin-bottom:20px;">📲 LLAMAR CHOFER</div></a>', unsafe_allow_html=True)
    else:
        st.info("No hay camiones reportados volviendo vacíos ahora.")
