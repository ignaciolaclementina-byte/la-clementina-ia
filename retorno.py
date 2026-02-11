import streamlit as st
import pandas as pd
import urllib.parse

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN BLINDADA (Lectura Directa) ---
# Usamos el modo exportación CSV que es infalible para leer
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=669889309"

# ESTILOS VISUALES
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

# LECTURA DE DATOS
try:
    df_cargas = pd.read_csv(URL_CARGAS)
    df_camiones = pd.read_csv(URL_CAMIONES)
except Exception:
    # Si falla, creamos tablas vacías para que no se rompa
    df_cargas = pd.DataFrame(columns=["origen", "item", "pago", "tel"])
    df_camiones = pd.DataFrame(columns=["nombre", "tel", "origen", "tipo"])

# TÍTULOS
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important;'>🍎 La Clementina - Logística</p>", unsafe_allow_html=True)

# CONTADORES
col1, col2 = st.columns(2)
col1.metric("📦 Cargas Hoy", len(df_cargas))
col2.metric("🚛 Camiones Ruta", len(df_camiones))

st.write("---")

tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR (WhatsApp)", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCADOR (Funciona automático con la planilla) ---
with tab1:
    filtro = st.selectbox("¿Desde dónde buscás?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    hay_datos = False
    for index, row in df_cargas.iterrows():
        # Filtro básico y limpieza de datos
        origen_dato = str(row['origen']) if pd.notna(row['origen']) else ""
        
        if filtro == "Todos" or origen_dato == filtro:
            hay_datos = True
            item = row['item'] if pd.notna(row['item']) else "Mercadería varia"
            pago = row['pago'] if pd.notna(row['pago']) else "A convenir"
            tel = str(row['tel']).replace(".0", "") if pd.notna(row['tel']) else ""
            
            st.markdown(f"""
            <div class='card-blanca'>
                <strong>📍 {origen_dato} → San Jorge</strong><br>
                <span>📦 {item}</span><br>
                <span style='color: #27ae60 !important;'>💰 PAGO: ${pago}</span>
            </div>
            """, unsafe_allow_html=True)
            
            msg = f"🚛 *RETORNO MATCH*\nHola! Vi tu carga de *{item}* en *{origen_dato}*. ¿Sigue disponible?"
            link = f"https://wa.me/549{tel}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank"><button style="width:100%; background-
