import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONFIGURACIÓN DE CONEXIÓN ---
ID_PLANILLA = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"

# Formato infalible para leer pestañas por nombre
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID_PLANILLA}/gviz/tq?tqx=out:csv&sheet=camiones"

# ESTILOS
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 6px solid #2ecc71; margin-bottom: 15px; }
    .card b { color: #2c3e50; font-size: 18px; }
    .card p { color: #555; margin: 5px 0; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# FUNCION PARA CARGAR DATOS SIN ERRORES
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower() # Limpia espacios y mayúsculas
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

df_cargas = cargar_datos(URL_CARGAS)
df_camiones = cargar_datos(URL_CAMIONES)

t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 MI CAMIÓN"])

# --- PESTAÑA 1: BUSCADOR ---
with t1:
    if not df_cargas.empty:
        # Buscador por Origen
        opciones = ["Todos"] + sorted(df_cargas['origen'].unique().tolist())
        filtro = st.selectbox("¿Desde dónde buscás?", opciones)
        
        for _, r in df_cargas.iterrows():
            if filtro == "Todos" or str(r['origen']) == filtro:
                st.markdown(f"""
                <div class='card'>
                    <b>📍 {r['origen']} → San Jorge</b>
                    <p>📦 Mercadería: {r['item']}</p>
                    <p>💰 Pago: ${r['pago']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón de WhatsApp
                tel = str(r['tel']).split('.')[0].replace(" ", "")
                msg = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
                st.markdown(f'<a href="https://wa.me/549{tel}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:8px; font-weight:bold; margin-top:-10px; margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No se encontraron datos. Revisá que la pestaña del Excel se llame 'cargas' y tenga datos abajo de los títulos.")
        st.info("Títulos requeridos en Excel: origen, item, pago, tel")

# --- PESTAÑA 2: PUBLICAR ---
with t2:
    st.subheader("Publicar nueva carga")
    with st.form("pub"):
        o = st.text_input("Origen (Ej: Rosario)")
        i = st.text_input("¿Qué mercadería es?")
        p = st.text_input("Pago ofrecido")
        if st.form_submit_button("🚀 GENERAR PUBLICACIÓN"):
            texto = urllib.parse.quote(f"NUEVA CARGA:\n📍 Origen: {o}\n📦 Item: {i}\n💰 Pago: {p}")
            st.markdown(f'<a href="https://wa.me/5493406433604?text={texto}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR A CENTRAL</div></a>', unsafe_allow_html=True)

# --- PESTAÑA 3: CAMIONES ---
with t3:
    if not df_camiones.empty:
        for _, r in df_camiones.iterrows():
            st.markdown(f"<div class='card'><b>🚛 {r['nombre']}</b><p>📍 Volviendo de: {r['origen']}</p></div>", unsafe_allow_html=True)
    else:
        st.info("No hay camiones reportados todavía.")
