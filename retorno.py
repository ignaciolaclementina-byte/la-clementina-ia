import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS "NIVEL DIOS" PARA EL FONDO Y DISEÑO PROFESIONAL
st.markdown("""
    <style>
    /* 1. ELIMINAR EL NEGRO DE STREAMLIT Y PONER LA IMAGEN DETRÁS DE TODO */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* 2. HACER QUE TODO LO DEMÁS SEA TRANSPARENTE */
    [data-testid="stVerticalBlock"], .main .block-container, div[class^="st-emotion-cache"] {
        background-color: transparent !important;
    }

    /* 3. TARJETAS CON EFECTO VIDRIO (GLASSMORPHISM) */
    .card {
        background: rgba(255, 255, 255, 0.9); /* Blanco casi opaco pero suave */
        backdrop-filter: blur(5px);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    .card-camion { border-left: 10px solid #25D366; }
    .card-carga { border-left: 10px solid #3498db; }

    /* 4. TEXTOS DE ALTA VISIBILIDAD */
    h1, h2, h3, p, span, label {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }
    
    .title-text { color: #1a1a1a !important; font-weight: 900; font-size: 24px; text-shadow: none; }
    .sub-text { color: #333 !important; font-size: 17px; text-shadow: none; font-weight: 500; }

    /* 5. DISEÑO DE PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: rgba(0,0,0,0.4);
        padding: 10px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        color: white !important;
        font-weight: bold;
        font-size: 18px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #25D366 !important;
        border-radius: 10px;
    }

    /* 6. BOTONES */
    .btn-wa { background-color: #25D366; color: white !important; padding: 12px 25px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 16px; }
    .btn-blue { background-color: #3498db; color: white !important; padding: 12px 25px; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO
st.markdown("<h1 style='text-align:center; font-size: 60px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-size: 22px; font-weight: bold; margin-top:-20px;'>LOGÍSTICA PROFESIONAL - SAN JORGE</p>", unsafe_allow_html=True)

# 4. PESTAÑAS
tab_chof, tab_emp = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- VISTA CHOFER ---
with tab_chof:
    st.markdown("### 🛠️ Herramientas para el Transportista")
    
    # EL FORMULARIO PARA CARGAR EL CAMIÓN
    with st.expander("📢 PUBLICAR MI CAMIÓN VACÍO (Clic aquí para cargar tus datos)"):
        with st.form("form_chofer"):
            c1, c2 = st.columns(2)
            with c1:
                ori = st.text_input("📍 ¿Desde dónde salís?")
                equ = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            with c2:
                des = st.text_input("🏁 ¿Hacia dónde vas?")
                tel = st.text_input("📱 Tu WhatsApp (Solo números)")
            
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                st.success("✅ ¡Publicado! Ahora las empresas te verán en su lista.")

    st.markdown("### 📦 Cargas disponibles que podés llevar")
    # Ejemplo de carga de una empresa
    st.markdown("""
        <div class="card card-carga">
            <div>
                <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                <p class="sub-text">📦 <b>CARGA:</b> 12 Pallets de mercadería | 🏢 <b>EMPRESA:</b> Logística San Jorge</p>
            </div>
            <a href="#" class="btn-blue">ACEPTAR VIAJE</a>
        </div>
    """, unsafe_allow_html=True)

# --- VISTA EMPRESA ---
with tab_emp:
    st.markdown("### 🚛 Camiones buscando retorno")
    
    # CONEXIÓN A TU GOOGLE SHEET (CAMIONES)
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel_num = "".join(filter(str.isdigit, str(row['tel'])))
            link_wa = f"https://wa.me/{tel_num}?text=Hola!%20Vi%20tu%20camion%20en%20Retorno%20Match"
            
            st.markdown(f"""
                <div class="card card-camion">
                    <div>
                        <p class="title-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                        <p class="sub-text">🚛 <b>EQUIPO:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                    </div>
                    <a href="{link_wa}" target="_blank" class="btn-wa">WHATSAPP</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando camiones en la base de datos...")

st.markdown("<br><hr><p style='text-align:center; opacity:0.7;'>Dashboard Logístico | San Jorge 2026</p>", unsafe_allow_html=True)
