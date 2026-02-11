import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# LINKS DIRECTOS (ID de tu planilla)
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=0"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=669889309"

# ESTILO
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 6px solid #2ecc71; margin-bottom: 10px; color: #2c3e50; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# CARGAR DATOS
try:
    df_cargas = pd.read_csv(URL_CARGAS).dropna(how='all')
    df_camiones = pd.read_csv(URL_CAMIONES).dropna(how='all')
except:
    df_cargas = pd.DataFrame()
    df_camiones = pd.DataFrame()

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important;'>La Clementina - San Jorge</p>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 MI CAMIÓN"])

with t1:
    f = st.selectbox("Filtrar origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    if not df_cargas.empty:
        for _, r in df_cargas.iterrows():
            if f == "Todos" or str(r['origen']) == f:
                st.markdown(f"<div class='card'><b>📍 {r['origen']} → San Jorge</b><br>📦 {r['item']}<br>💰 ${r['pago']}</div>", unsafe_allow_html=True)
                txt = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
                link = f"https://wa.me/549{str(r['tel']).split('.')[0]}?text={txt}"
                st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)
    else:
        st.info("No hay cargas registradas en el Excel.")

with t2:
    with st.form("c"):
        i = st.text_input("¿Qué mercadería es?")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        p = st.text_input("Pago ofrecido")
        if st.form_submit_button("🚀 PREPARAR MENSAJE"):
            m = urllib.parse.quote(f"NUEVA CARGA:\n- Origen: {o}\n- Item: {i}\n- Pago: {p}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</div></a>', unsafe_allow_html=True)

with t3:
    with st.form("cam"):
        n = st.text_input("Nombre / Empresa")
        v = st.selectbox("Vuelvo de", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        if st.form_submit_button("📢 AVISAR RETORNO"):
            m2 = urllib.parse.quote(f"CAMIÓN DISPONIBLE:\n- Empresa: {n}\n- Vuelve de: {v}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m2}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 AVISAR A CENTRAL</div></a>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🚛 Camiones en ruta")
    if not df_camiones.empty:
        for _, r in df_camiones.iterrows():
            st.markdown(f"<div class='card'><b>🚛 {r['nombre']}</b><br>📍 Volviendo de {r['origen']}</div>", unsafe_allow_html=True)
    else:
        st.info("No hay camiones avisados.")
