import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA (DEBE SER LO PRIMERO)
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS "BLINDADO" PARA EL FONDO
st.markdown("""
    <style>
    /* Aplicar fondo a absolutamente todas las capas posibles */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* Quitar el color negro de los contenedores de Streamlit */
    div[class^="st-emotion-cache"], .main .block-container {
        background-color: transparent !important;
    }

    /* Estilo de Tarjetas */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    }
    .card-camion { border-left: 10px solid #25D366; }
    .card-carga { border-left: 10px solid #3498db; }

    /* Forzar color de textos fuera de las tarjetas */
    h1, h2, h3, p, label, .stMarkdown {
        color: white !important;
    }
    
    /* Textos dentro de las tarjetas (deben ser oscuros para leerse bien) */
    .title-text { color: #1a1a1a !important; font-weight: 800; font-size: 22px; margin:0; }
    .sub-text { color: #444 !important; font-size: 16px; margin: 5px 0; }

    /* Botones */
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }
    .btn-blue { background-color: #3498db; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; }

    /* Ajuste de Pestañas */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white !important; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<h1 style='text-align:center; font-size: 50px; margin-bottom:0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-weight:bold;'>LOGÍSTICA SAN JORGE - CONECTANDO CARGAS</p>", unsafe_allow_html=True)

# 4. PESTAÑAS
tab1, tab2 = st.tabs(["🚚 BUSCAR CARGA (Para Choferes)", "📦 BUSCAR CAMIÓN (Para Empresas)"])

with tab1:
    st.markdown("### 🏢 Cargas que necesitan camión")
    with st.expander("📢 PUBLICAR CARGA (Solo Empresas)"):
        st.write("Formulario para empresas aquí...")
    
    # Ejemplo de tarjeta de carga
    st.markdown("""
        <div class="card card-carga">
            <div>
                <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                <p class="sub-text">📦 <b>CARGA:</b> 15 Pallets de mercadería | 🏢 <b>EMPRESA:</b> Distribuidora S.J.</p>
            </div>
            <a href="#" class="btn-blue">ACEPTAR CARGA</a>
        </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("### 🚛 Camiones disponibles en la zona")
    
    # Lectura de tu Google Sheet actual
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link = f"https://wa.me/{tel}?text=Hola!%20Vi%20tu%20camion"
            st.markdown(f"""
                <div class="card card-camion">
                    <div>
                        <p class="title-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                        <p class="sub-text">🚛 <b>EQUIPO:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                    </div>
                    <a href="{link}" target="_blank" class="btn-wa">WHATSAPP</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando camiones...")

st.markdown("<br><p style='text-align:center; opacity:0.6;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
