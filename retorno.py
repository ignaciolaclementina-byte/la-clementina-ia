import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# LINKS DE TU PLANILLA (Lectura directa sin contraseñas)
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=0"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/export?format=csv&gid=669889309"

# ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 6px solid #2ecc71; margin-bottom: 10px; color: #2c3e50; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# CARGAR DATOS
try:
    df_cargas = pd.read_csv(URL_CARGAS)
    df_camiones = pd.read_csv(URL_CAMIONES)
except:
    df_cargas = pd.DataFrame(columns=["origen", "item", "pago", "tel"])
    df_camiones = pd.DataFrame(columns=["nombre", "tel", "origen", "tipo"])

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important;'>La Clementina - San Jorge</p>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 MI CAMIÓN"])

with t1:
    f = st.selectbox("Filtrar origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    for _, r in df_cargas.iterrows():
        if f == "Todos" or str(r['origen']) == f:
            st.markdown(f"<div class='card'><b>📍 {r['origen']} → San Jorge</b><br>📦 {r['item']}<br>💰 ${r['pago']}</div>", unsafe_allow_html=True)
            txt = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
            link = f"https://wa.me/549{str(r['tel']).replace('.0','')}?text={txt}"
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">📲 CONTACTAR</button></a>', unsafe_allow_html=True)

with t2:
    with st.form("c"):
        i = st.text_input("¿Qué llevamos?")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        p = st.number_input("Pago ($)", step=1000)
        if st.form_submit_button("🚀 PREPARAR"):
            m = urllib.parse.quote(f"NUEVA CARGA:\n- Origen: {o}\n- Item: {i}\n- Pago: ${p}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</button></a>', unsafe_allow_html=True)

with t3:
    with st.form("cam"):
        n = st.text_input("Nombre / Empresa")
        v = st.selectbox("Vuelvo de", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        if st.form_submit_button("📢 AVISAR"):
            m2 = urllib.parse.quote(f"CAMIÓN DISPONIBLE:\n- Empresa: {n}\n- Vuelve de: {v}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m2}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold;">📲 AVISAR A CENTRAL</button></a>', unsafe_allow_html=True)
