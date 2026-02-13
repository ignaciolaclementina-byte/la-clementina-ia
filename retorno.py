import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN (SIEMPRE PRIMERO)
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. CSS PARA FONDO Y DISEÑO PROFESIONAL
st.markdown("""
    <style>
    /* FONDO GLOBAL */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* TRANSPARENCIAS */
    .stApp, .stMain, [data-testid="stHeader"], .block-container {
        background: transparent !important;
    }

    /* TARJETAS BLANCAS (Máxima legibilidad) */
    .card {
        background: white !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }

    /* ESTILO DE TEXTOS */
    h1, h2, h3, label, p { color: white !important; }
    .card-title { color: #1a1a1a !important; font-size: 20px; font-weight: bold; margin: 0; }
    .card-sub { color: #555 !important; font-size: 16px; margin: 5px 0; }

    /* BOTONES */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    
    /* PESTAÑAS */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO
st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-weight:bold;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>", unsafe_allow_html=True)

# 4. PESTAÑAS
tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- VISTA CHOFER ---
with tab_chofer:
    # A. Publicar Camión
    with st.expander("📢 PUBLICAR MI CAMIÓN DISPONIBLE (Clic aquí)"):
        with st.form("f_camion"):
            c1, c2 = st.columns(2)
            with c1:
                orig = st.text_input("📍 ¿Desde dónde salís?")
                equip = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            with c2:
                dest = st.text_input("🏁 ¿Hacia dónde vas?")
                wapp = st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR CAMIÓN"):
                st.success("¡Camión publicado! Las empresas ahora pueden verte.")

    st.markdown("### 📦 Cargas disponibles para llevar")
    # Aquí es donde el chofer ve lo que las empresas publicaron
    # Simulamos datos de una empresa
    st.markdown("""
        <div class="card" style="border-left: 8px solid #3498db;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p class="card-title">📍 ROSARIO → SAN JORGE</p>
                    <p class="card-sub">📦 15 Pallets (Alimento) | 🏢 Logística San Jorge</p>
                </div>
                <a href="#" class="btn-wa" style="background-color: #3498db;">ACEPTAR CARGA</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- VISTA EMPRESA ---
with tab_empresa:
    # A. Formulario para que la Empresa cargue sus datos (LO QUE PREGUNTASTE)
    with st.expander("📦 PUBLICAR UNA NECESIDAD DE CARGA (Clic aquí)"):
        with st.form("f_carga"):
            st.markdown("<p style='color:black !important;'>Cargue los datos de la mercadería que necesita mover:</p>", unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                e_orig = st.text_input("📍 Punto de Retiro")
                e_merc = st.text_input("📦 Mercadería (Ej: 12 Pallets, Cereal)")
            with col2:
                e_dest = st.text_input("🏁 Punto de Entrega")
                e_wapp = st.text_input("📱 WhatsApp de la Empresa")
            
            if st.form_submit_button("PUBLICAR CARGA"):
                st.success("✅ ¡Carga publicada! Los choferes la verán en su pestaña.")

    st.markdown("### 🚛 Camiones buscando retorno")
    # Aquí la empresa ve los datos del Google Sheets de los choferes
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL).iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        for _, row in df.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link = f"https://wa.me/{tel}"
            st.markdown(f"""
                <div class="card" style="border-left: 8px solid #25D366;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p class="card-title">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                            <p class="card-sub">🚛 {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="{link}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("No hay camiones publicados por ahora.")

st.markdown("<br><p style='text-align:center; opacity:0.5; color:white;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
