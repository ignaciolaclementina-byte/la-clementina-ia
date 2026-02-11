import streamlit as st
import urllib.parse

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2ecc71;
        margin-bottom: 15px;
    }
    .card-blanca * { color: #2c3e50 !important; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #2ecc71; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS EN SESIÓN
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA CON CONTADORES
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important; font-size: 20px;'>🍎 La Clementina - Logística</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Disponibles", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones en Ruta", len(st.session_state.camiones))

st.write("---")

# 4. PESTAÑAS
tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR CARGA", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCADOR ---
with tab1:
    filtro = st.selectbox("¿Desde dónde buscás carga?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    hay_algo = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            hay_algo = True
            st.markdown(f"""
                <div class='card-blanca'>
                    <strong>📍 {c['origen']} → San Jorge</strong><br>
                    <span>📦
