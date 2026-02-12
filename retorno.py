import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN VISUAL (FONDO Y ESTILO PRO)
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    /* Fondo de depósito logístico oscuro */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    
    /* Estilo de las pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; color: white !important; font-weight: bold; border: 1px solid rgba(255,255,255,0.2); border-radius: 5px; }
    .stTabs [aria-selected="true"] { background-color: #2ecc71 !important; border-color: #2ecc71 !important; }

    /* Tarjetas de resultados */
    .card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 8px solid #2ecc71; color: black; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .card-camion { border-left: 8px solid #3498db; }
    .card h3 { margin-top:0; color: #1a1a1a; font-size: 1.2rem; font-weight: 800; }
    .card p { margin: 5px 0; color: #444; font-size: 0.95rem; }

    /* Botones */
    .btn-ws { display: block; width: 100%; text-align: center; background: #25D366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; }
    .btn-ws:hover { background: #1da851; }
    
    /* Títulos */
    h1 { color: white !important; text-align: center; font-weight: 900; letter-spacing: 2px; text-transform: uppercase; }
    .seccion-titulo { color: #2ecc71; font-weight: bold; margin-bottom: 10px; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A BASE DE DATOS (LECTURA)
# Usamos tu link CSV público que ya funcionaba
URL_DATOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv&gid=0"
URL_CAMIONES = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv&gid=1752528761"

# Tu número de Admin para recibir las solicitudes de publicación
ADMIN_WHATSAPP = "5493406649346" 

def cargar_db(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

# 3. INTERFAZ PRINCIPAL
st.markdown("<h1>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab_buscar, tab_pub_carga, tab_pub_camion = st.tabs(["🔍 BUSCAR", "📦 PUBLICAR CARGA", "🚛 PUBLICAR CAMIÓN"])

# --- PESTAÑA 1: BUSCADOR ---
with tab_buscar:
    col1, col2 = st.columns([3, 1])
    with col1:
        filtro = st.text_input("📍 Filtrar por Ciudad:", placeholder="Ej: Rosario, Rafaela...", key="search")
    with col2:
        if st.button("🔄 ACTUALIZAR"):
            st.cache_data.clear()
            st.rerun()
