import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS AVANZADO (Manteniendo tu estructura solicitada)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp, .stMain, [data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 2rem !important; }

    /* Estilo de Pestañas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: rgba(255,255,255,0.1); border-radius: 10px; color: white !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; }

    /* TARJETAS */
    .card-container {
        background: white !important;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .info-section { flex-grow: 1; }
    .route-text { font-size: 22px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 15px; color: #555 !important; margin-top: 5px; }

    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        white-space: nowrap;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER
st.markdown("""
    <div style='text-align:center; padding-bottom: 20px;'>
        <h1 style='font-size: 45px; color: white; margin-bottom:0;'>🚛 RETORNO MATCH</h1>
        <p style='color: #25D366; font-size: 18px; font-weight: bold; letter-spacing: 2px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>
    </div>
    """, unsafe_allow_html=True)

# 4. DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# URL Cargas (Hoja 4)
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%204&t={int(time.time())}"
# URL Camiones (Hoja 3)
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- VISTA CHOFER ---
with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 📢 Mi disponibilidad")
        st.info("Completá el formulario de camiones para aparecer en la lista de empresas.")
        # Aquí iría el link a tu formulario de camiones
        st.link_button("CARGAR MI CAMIÓN", "TU_LINK_DE_FORMULARIO_3", use_container_width=True)

    with col_b:
        st.markdown("### 📦 Cargas disponibles")
        try:
            df_c = pd.read_csv(URL_CARGAS).iloc[:, :5]
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            for _, row in df_c.iloc[::-1].iterrows():
                tel = "".join(filter(str.isdigit, str(row['tel'])))
                st.markdown(f"""
                    <div class="card-container" style="border-left: 10px solid #3498db;">
                        <div class="info-section">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">📦 <b>Carga:</b> {row['mercaderia']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{tel}" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.write("Esperando nuevas cargas de empresas...")

# --- VISTA EMPRESA ---
with tab2:
    col_c, col_d = st.columns([1, 2])
    with col_c:
        st.markdown("### 📢 Publicar Carga")
        st.info("Publicá tu necesidad de transporte aquí.")
        # Aquí iría el link a tu formulario de cargas (Formulario 4)
        st.link_button("PUBLICAR CARGA", "TU_LINK_DE_FORMULARIO_4", use_container_width=True)

    with col_d:
        st.markdown("### 🚛 Camiones buscando retorno")
        try:
            df_v = pd.read_csv(URL_CAMIONES).iloc[:, :5]
            df_v.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            for _, row in df_v.iloc[::-1].iterrows():
                tel = "".join(filter(str.isdigit, str(row['tel'])))
                st.markdown(f"""
                    <div class="card-container" style="border-left: 10px solid #25D366;">
                        <div class="info-section">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">🚛 <b>Equipo:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{tel}" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.write("Buscando camiones disponibles...")

st.markdown("<br><p style='text-align:center; color:white;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
