import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS AVANZADO (Diseño Moderno y Limpio)
st.markdown("""
    <style>
    /* Fondo con overlay más suave para lectura */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    
    .stApp, .stMain, [data-testid="stHeader"] { background: transparent !important; }

    /* Contenedor Principal */
    .block-container { padding-top: 2rem !important; }

    /* Estilo de Pestañas Modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px;
        color: white !important;
        font-weight: bold;
        transition: 0.3s;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #25D366 !important;
        transform: scale(1.02);
    }

    /* TARJETAS MEJORADAS */
    .card-container {
        background: white !important;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
        border-left: 10px solid #25D366;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .info-section { flex-grow: 1; }
    
    .route-text {
        font-size: 22px;
        font-weight: 800;
        color: #1a1a1a !important;
        margin: 0;
        display: flex;
        align-items: center;
    }
    
    .detail-text {
        font-size: 15px;
        color: #555 !important;
        margin-top: 5px;
    }

    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
        transition: 0.3s;
        white-space: nowrap;
    }
    
    .btn-wa:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(37, 211, 102, 0.5); }

    /* Formulario Estilizado */
    .stForm {
        background: rgba(255,255,255,0.05);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER PROFESIONAL
st.markdown("""
    <div style='text-align:center; padding-bottom: 20px;'>
        <h1 style='font-size: 45px; color: white; margin-bottom:0;'>🚛 RETORNO MATCH</h1>
        <p style='color: #25D366; font-size: 18px; font-weight: bold; letter-spacing: 2px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>
    </div>
    """, unsafe_allow_html=True)

# 4. NAVEGACIÓN PRINCIPAL
tab1, tab2 = st.tabs(["👋 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- SECCIÓN CHOFER ---
with tab1:
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_camion", clear_on_submit=True):
            orig = st.text_input("📍 Origen", placeholder="Ej: San Jorge")
            dest = st.text_input("🏁 Destino", placeholder="Ej: Rosario")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            tel = st.text_input("📱 WhatsApp", placeholder="3406123456")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                st.success("¡Camión publicado!")

    with col_b:
        st.markdown("### 📦 Cargas esperando transporte")
        # Esto debería venir de tu hoja de Google Sheets (Cargas)
        # Ejemplo visual de como quedaría:
        st.markdown(f"""
            <div class="card-container" style="border-left-color: #3498db;">
                <div class="info-section">
                    <p class="route-text">📍 ROSARIO ➔ SAN JORGE</p>
                    <p class="detail-text">📦 <b>Carga:</b> 12 Pallets Mercadería | 🏢 Logística SJ</p>
                </div>
                <a href="https://wa.me/3406000000" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
            </div>
        """, unsafe_allow_html=True)

# --- SECCIÓN EMPRESA ---
with tab2:
    col_c, col_d = st.columns([1, 2])
    
    with col_c:
        st.markdown("### 📢 Publicar Carga")
        with st.form("form_carga", clear_on_submit=True):
            e_orig = st.text_input("📍 Punto de Retiro")
            e_dest = st.text_input("🏁 Punto de Entrega")
            e_merc = st.text_input("📦 ¿Qué mercadería es?")
            e_tel = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("BUSCAR CAMIÓN AHORA", use_container_width=True):
                st.success("¡Carga publicada!")

    with col_d:
        st.markdown("### 🚛 Camiones buscando retorno")
        # CONEXIÓN REAL CON TU SHEETS
        SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
        URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
        
        try:
            df = pd.read_csv(URL).iloc[:, :5]
            df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            for _, row in df.iloc[::-1].head(10).iterrows():
                tel_clean = "".join(filter(str.isdigit, str(row['tel'])))
                st.markdown(f"""
                    <div class="card-container">
                        <div class="info-section">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">🚛 <b>Equipo:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{tel_clean}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.warning("Conectando con la base de datos de camiones...")

st.markdown("<br><p style='text-align:center; color:gray;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
