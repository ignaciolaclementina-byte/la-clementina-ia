import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS "FUERZA BRUTA" PARA EL FONDO Y TRANSPARENCIAS
st.markdown("""
    <style>
    /* ESTO ELIMINA EL FONDO NEGRO DE TODAS LAS CAPAS */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"], [data-testid="stVerticalBlock"] {
        background: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* FORZAR TRANSPARENCIA EN CONTENEDORES INTERNOS */
    div[class^="st-emotion-cache"], .main .block-container {
        background-color: transparent !important;
    }

    /* TARJETAS ESTILO PREMIUM */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .card-camion { border-left: 10px solid #25D366; }
    .card-carga { border-left: 10px solid #3498db; }

    /* TEXTOS */
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    .title-text { color: #1a1a1a !important; font-weight: 800; font-size: 22px; margin: 0; }
    .sub-text { color: #444 !important; font-size: 16px; margin: 5px 0; }

    /* BOTONES */
    .btn-wa { background-color: #25D366; color: white !important; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: bold; }
    .btn-blue { background-color: #3498db; color: white !important; padding: 12px 24px; border-radius: 10px; text-decoration: none; font-weight: bold; }

    /* DISEÑO DE PESTAÑAS */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 12px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<h1 style='text-align:center; font-size: 55px; font-weight: 900; margin-bottom:0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-size: 20px; font-weight: bold;'>LOGÍSTICA SAN JORGE — CONECTANDO CARGAS</p>", unsafe_allow_html=True)

# 4. SISTEMA DE PESTAÑAS
tab_choferes, tab_empresas = st.tabs(["🚀 PARA CHOFERES (Buscá Carga)", "🏭 PARA EMPRESAS (Buscá Camión)"])

# --- PESTAÑA 1: EL CHOFER ENTRA ACÁ ---
with tab_choferes:
    st.markdown("### 🏢 Cargas Disponibles (Empresas que necesitan camión)")
    
    # Formulario para que el chofer publique su camion (NUEVA UBICACIÓN CLARA)
    with st.expander("📝 PUBLICAR MI CAMIÓN DISPONIBLE (Choferes completar aquí)"):
        with st.form("form_nuevo_camion", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                ori = st.text_input("📍 Origen (Desde donde salís)")
                equ = st.selectbox("🚛 Tipo de Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            with c2:
                des = st.text_input("🏁 Destino (A donde vas)")
                tel = st.text_input("📱 Tu WhatsApp (Ej: 3406123456)")
            
            if st.form_submit_button("🚀 PUBLICAR MI CAMIÓN"):
                if ori and des and tel:
                    # Aquí iría tu link de Google Form actual
                    st.success("✅ ¡Publicado! Ahora las empresas te verán en la otra pestaña.")
                else:
                    st.warning("Completá los datos.")

    st.write("---")
    # Ejemplo de carga que el chofer puede ver
    st.markdown("""
        <div class="card card-carga">
            <div>
                <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                <p class="sub-text">📦 <b>CARGA:</b> 15 Pallets de mercadería | 🏢 <b>EMPRESA:</b> Distribuidora S.J.</p>
            </div>
            <a href="#" class="btn-blue">ACEPTAR CARGA</a>
        </div>
    """, unsafe_allow_html=True)

# --- PESTAÑA 2: LA EMPRESA ENTRA ACÁ ---
with tab_empresas:
    st.markdown("### 🚛 Camiones Disponibles (Choferes buscando retorno)")
    
    with st.expander("📢 PUBLICAR CARGA (Si sos una empresa y necesitás un camión)"):
        st.info("Formulario para empresas en desarrollo...")

    # CARGA DE DATOS REALES DE TU EXCEL (Tu lista actual)
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel_clean = "".join(filter(str.isdigit, str(row['tel'])))
            link = f"https://wa.me/{tel_clean}?text=Hola!%20Vi%20tu%20camion%20en%20Retorno%20Match"
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
        st.write("Actualizando lista de camiones...")

st.markdown("<br><p style='text-align:center; opacity:0.6;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
