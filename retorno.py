import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN ---
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Forzamos la lectura de las solapas por nombre
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# CARGA DE DATOS CON MODO DIAGNÓSTICO
try:
    df_cargas = pd.read_csv(URL_CARGAS)
    df_camiones = pd.read_csv(URL_CAMIONES)
    
    # Si logramos leer, limpiamos filas vacías
    df_cargas = df_cargas.dropna(subset=['origen', 'item'])
except Exception as e:
    st.error(f"❌ ERROR DE LECTURA: {e}")
    st.info("Revisá que en el Excel las solapas se llamen 'cargas' y 'camiones' exactamente.")
    st.stop()

# INTERFAZ
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 MI CAMIÓN"])

with t1:
    f = st.selectbox("Filtrar origen:", ["Todos"] + sorted(df_cargas['origen'].unique().tolist()) if not df_cargas.empty else ["Todos"])
    
    if df_cargas.empty:
        st.warning("⚠️ El Excel parece estar vacío. Agregá una fila en la pestaña 'cargas'.")
    else:
        for _, r in df_cargas.iterrows():
            if f == "Todos" or str(r['origen']) == f:
                st.markdown(f"""
                <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2ecc71;">
                    <b style="color: #2c3e50;">📍 {r['origen']} → San Jorge</b><br>
                    <span style="color: #2c3e50;">📦 {r['item']} | 💰 ${r['pago']}</span>
                </div>
                """, unsafe_allow_html=True)
                txt = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
                st.markdown(f'<a href="https://wa.me/549{str(r["tel"]).split(".")[0]}?text={txt}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold; margin-bottom:20px;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)

with t2:
    st.write("### Publicar Nueva Carga")
    # (El resto del formulario de WhatsApp que ya tenías...)
    with st.form("pub"):
        orig = st.text_input("Origen")
        item = st.text_input("Mercadería")
        pago = st.text_input("Pago")
        if st.form_submit_button("PREPARAR"):
            m = urllib.parse.quote(f"NUEVA CARGA:\n- Origen: {orig}\n- Item: {item}\n- Pago: {pago}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={m}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</div></a>', unsafe_allow_html=True)
