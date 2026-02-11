import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- SOLUCIÓN DEFINITIVA: LINK DIRECTO ---
# Al poner el link acá, saltamos el error de configuración de Secrets
URL_PLANILLA = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 15px;
        border-radius: 12px;
        border-left: 8px solid #2ecc71;
        margin-bottom: 10px;
    }
    .card-blanca * { color: #2c3e50 !important; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

# LECTURA FORZADA CON LINK EXPLICITO
try:
    df_cargas = conn.read(spreadsheet=URL_PLANILLA, worksheet="cargas", ttl="0s")
    df_camiones = conn.read(spreadsheet=URL_PLANILLA, worksheet="camiones", ttl="0s")
except Exception as e:
    st.error(f"⚠️ ERROR CRÍTICO: {e}")
    st.stop()

# CABECERA
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important;'>🍎 La Clementina - Logística</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
col1.metric("📦 Cargas Hoy", len(df_cargas))
col2.metric("🚛 Camiones Ruta", len(df_camiones))

st.write("---")

tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR CARGA", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCAR ---
with tab1:
    filtro = st.selectbox("¿Desde dónde buscás?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    for index, row in df_cargas.iterrows():
        if filtro == "Todos" or row['origen'] == filtro:
            st.markdown(f"<div class='card-blanca'><strong>📍 {row['origen']} → San Jorge</strong><br><span>📦 {row['item']}</span><br><span style='color: #27ae60 !important;'>PAGO: ${row['pago']}</span></div>", unsafe_allow_html=True)
            msg = f"🚛 *RETORNO MATCH*\nHola! Vi tu carga de *{row['item']}* en *{row['origen']}*. ¿Sigue disponible?"
            link = f"https://wa.me/54{row['tel']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)

# --- TAB 2: PUBLICAR CARGA ---
with tab2:
    with st.form("form_carga", clear_on_submit=True):
        i = st.text_input("¿Qué mercadería?")
        t = st.text_input("WhatsApp")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        p = st.number_input("Pago ofrecido ($)", min_value=0, step=1000)
        
        if st.form_submit_button("🚀 PUBLICAR"):
            if i and t:
                new_row = pd.DataFrame([{"origen": o, "item": i, "pago": p, "tel": t}])
                updated_df = pd.concat([df_cargas, new_row], ignore_index=True)
                conn.update(spreadsheet=URL_PLANILLA, worksheet="cargas", data=updated_df)
                st.success("✅ ¡Publicado!")
                st.rerun()

# --- TAB 3: PUBLICAR CAMIÓN ---
with tab3:
    with st.form("form_camion", clear_on_submit=True):
        n = st.text_input("Nombre / Empresa")
        tc = st.text_input("WhatsApp")
        oc = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        tp = st.selectbox("Tipo de unidad", ["Chasis solo", "Acoplado", "Sider", "Térmico"])
        
        if st.form_submit_button("📢 PUBLICAR VUELTA"):
            if n and tc:
                new_cam = pd.DataFrame([{"nombre": n, "tel": tc, "origen": oc, "tipo": tp}])
                updated_cam = pd.concat([df_camiones, new_cam], ignore_index=True)
                conn.update(spreadsheet=URL_PLANILLA, worksheet="camiones", data=updated_cam)
                st.success("✅ ¡Camión guardado!")
                st.rerun()

    st.write("---")
    for index, row in df_camiones.iterrows():
        st.markdown(f"<div class='card-blanca'><strong>🚛 {row['nombre']}</strong><br><span>📍 Vuelve de: {row['origen']}</span><br><span>⚙️ {row['tipo']}</span></div>", unsafe_allow_html=True)
