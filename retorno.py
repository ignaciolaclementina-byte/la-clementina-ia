import streamlit as st
import pandas as pd
import requests

# CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# ESTILO
st.markdown("""
    <style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; border-left: 10px solid #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

# URL DE LECTURA (Tu link de publicación)
URL_LECTURA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# URL DE ESCRITURA (La que vas a crear en el Paso 2)
URL_SCRIPT = "TU_URL_DE_GOOGLE_SCRIPT_AQUI"

st.title("🚛 RETORNO MATCH")
t1, t2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with t1:
    try:
        df = pd.read_csv(URL_LECTURA)
        for _, r in df.dropna(subset=[df.columns[0]]).iterrows():
            st.markdown(f"<div class='card'><h3>📍 {str(r.iloc[0]).upper()}</h3><p>{r.iloc[1]}</p><p><b>Tel:</b> {r.iloc[3]}</p></div>", unsafe_allow_html=True)
    except: st.info("Cargando...")

with t2:
    with st.form("nuevo_viaje"):
        origen = st.text_input("Origen")
        detalle = st.text_input("Detalle")
        pago = st.text_input("Pago")
        tel = st.text_input("WhatsApp")
        if st.form_submit_button("🚀 PUBLICAR"):
            # Mandamos los datos al Script de Google
            res = requests.post(URL_SCRIPT, json={"origen": origen, "detalle": detalle, "pago": pago, "tel": tel})
            if res.status_code == 200:
                st.success("✅ ¡Publicado! (Refrescá en 5 seg)")
                st.balloons()
            else: st.error("Error al publicar.")
