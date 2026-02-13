import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS AVANZADO (Dashboard Dual)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }

    /* Estilo de Tarjetas */
    .card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        transition: 0.3s;
    }
    .card-camion { border-left: 10px solid #25D366; } /* Verde para Camiones */
    .card-carga { border-left: 10px solid #3498db; }  /* Azul para Empresas/Cargas */

    .title-text { font-size: 22px; font-weight: 900; color: #1a1a1a !important; margin: 0; }
    .sub-text { color: #444 !important; font-size: 15px; margin: 5px 0; }
    
    /* Botones */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
    }
    .btn-contactar {
        background-color: #3498db;
        color: white !important;
        padding: 12px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
    }

    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px 10px 0 0;
        color: white;
        padding: 10px 30px;
    }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<h1 style='text-align:center; color:white; font-size: 50px; margin-bottom:0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366; font-weight:bold;'>SISTEMA INTEGRAL DE LOGÍSTICA SAN JORGE</p>", unsafe_allow_html=True)

# 4. SISTEMA DE PESTAÑAS
tab1, tab2 = st.tabs(["🚚 BUSCAR CARGA (Para Choferes)", "📦 BUSCAR CAMIÓN (Para Empresas)"])

# --- PESTAÑA 1: EMPRESAS PUBLICAN CARGAS ---
with tab1:
    st.markdown("<h3 style='color:white;'>🏢 Cargas Disponibles</h3>", unsafe_allow_html=True)
    st.info("Aquí los choferes pueden ver qué mercadería necesita transporte.")
    
    with st.expander("📢 PUBLICAR NECESIDAD DE CARGA (Para Empresas)"):
        with st.form("form_carga_empresa"):
            c1, c2 = st.columns(2)
            with c1:
                carga_ori = st.text_input("📍 Desde dónde se retira")
                carga_tipo = st.text_input("📦 Qué mercadería es (ej: Pallets, cereal)")
            with c2:
                carga_des = st.text_input("🏁 Destino de la carga")
                carga_tel = st.text_input("📱 WhatsApp de contacto de la Empresa")
            
            if st.form_submit_button("PUBLICAR CARGA"):
                st.success("Carga publicada (conectalo a tu Google Sheet de Cargas)")

    # Aquí iría la lectura de la "Hoja 4" (Cargas)
    st.markdown("""
        <div class="card card-carga">
            <div>
                <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                <p class="sub-text">📦 <b>CARGA:</b> 12 Pallets de repuestos | 🏢 <b>EMPRESA:</b> Logística Norte</p>
            </div>
            <a href="#" class="btn-contactar">ACEPTAR VIAJE</a>
        </div>
    """, unsafe_allow_html=True)

# --- PESTAÑA 2: CHOFERES PUBLICAN CAMIONES (Lo que ya tenías) ---
with tab2:
    st.markdown("<h3 style='color:white;'>🚛 Camiones Disponibles</h3>", unsafe_allow_html=True)
    
    with st.expander("📝 PUBLICAR MI CAMIÓN VACÍO (Para Choferes)"):
        with st.form("form_camion_chofer"):
            # ... (Tus campos de siempre)
            st.form_submit_button("PUBLICAR CAMIÓN")

    # CARGA DE DATOS DESDE GOOGLE (Tu código actual)
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link_wa = f"https://wa.me/{tel}?text=Hola!%20Vi%20tu%20camion"
            st.markdown(f"""
                <div class="card card-camion">
                    <div>
                        <p class="title-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                        <p class="sub-text">🚛 <b>EQUIPO:</b> {row['equipo']}</p>
                    </div>
                    <a href="{link_wa}" target="_blank" class="btn-wa">CONTACTAR</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("Cargando listado...")

st.markdown("<br><p style='text-align:center; color:white; opacity:0.5;'>Retorno Match v2.0 | Dashboard Profesional</p>", unsafe_allow_html=True)
