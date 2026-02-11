import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN DIRECTA ---
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Este link busca la pestaña por nombre exacto
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# ESTILO
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 6px solid #2ecc71; margin-bottom: 10px; color: #2c3e50; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# LECTURA CON DIAGNÓSTICO
try:
    df_cargas = pd.read_csv(URL_CARGAS).dropna(how='all')
    df_camiones = pd.read_csv(URL_CAMIONES).dropna(how='all')
except Exception as e:
    st.error(f"❌ ERROR DE LECTURA: {e}")
    st.stop()

t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 MI CAMIÓN"])

with t1:
    f = st.selectbox("Filtrar origen:", ["Todos"] + sorted(df_cargas['origen'].unique().tolist()) if not df_cargas.empty else ["Todos"])
    
    if df_cargas.empty:
        st.warning("⚠️ El Excel está conectado pero no hay datos cargados en la pestaña 'cargas'.")
    else:
        for _, r in df_cargas.iterrows():
            if f == "Todos" or str(r['origen']) == f:
                st.markdown(f"<div class='card'><b>📍 {r['origen']} → San Jorge</b><br>📦 {r['item']}<br>💰 ${r['pago']}</div>", unsafe_allow_html=True)
                txt = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
                link = f"https://wa.me/549{str(r['tel']).split('.')[0]}?text={txt}"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold; margin-bottom:20px;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)

with t2:
    with st.form("pub"):
        orig = st.text_input("Origen")
        item = st.text_input("Mercadería")
        pago = st.text_input("Pago")
        if st.form_submit_button("🚀 PREPARAR MENSAJE"):
            m = urllib.parse.quote(f"NUEVA CARGA:\n- Origen: {orig}\n- Item: {item}\n- Pago: {pago}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</div></a>', unsafe_allow_html=True)

with t3:
    st.write("---")
    if not df_camiones.empty:
        for _, r in df_camiones.iterrows():
            st.markdown(f"<div class='card'><b>🚛 {r['nombre']}</b><br>📍 Volviendo de {r['origen']}</div>", unsafe_allow_html=True)
    else:
        st.info("No hay camiones en ruta registrados.")
