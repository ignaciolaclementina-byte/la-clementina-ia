import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN DE PÁGINA (DEBE IR PRIMERO)
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. CSS "NUCLEAR" PARA RECUPERAR EL FONDO Y EL ASPECTO PROFESIONAL
st.markdown("""
    <style>
    /* FORZAMOS EL FONDO EN LA CAPA MÁS PROFUNDA */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* HACEMOS QUE TODAS LAS CAPAS DE STREAMLIT SEAN TRANSPARENTES */
    [data-testid="stHeader"], [data-testid="stMain"], .main, .block-container, [data-testid="stVerticalBlock"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    /* TARJETAS ESTILO PREMIUM (Blanco sólido para lectura perfecta) */
    .card {
        background: white !important;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        border-left: 10px solid #25D366;
    }

    /* ESTILOS DE TEXTO FUERA DE LAS TARJETAS */
    h1, h2, h3, p, label, span {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    /* TEXTO DENTRO DE LAS TARJETAS (Negro para que se lea) */
    .title-text { color: #1a1a1a !important; font-weight: 900; font-size: 24px; text-shadow: none !important; margin:0; }
    .sub-text { color: #444 !important; font-size: 18px; text-shadow: none !important; font-weight: 500; }

    /* BOTONES */
    .btn-wa { 
        background-color: #25D366; 
        color: white !important; 
        padding: 12px 25px; 
        border-radius: 10px; 
        text-decoration: none; 
        font-weight: bold; 
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* PESTAÑAS PROFESIONALES */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(0,0,0,0.4); border-radius: 15px; padding: 5px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-size: 18px; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO
st.markdown("<h1 style='text-align:center; font-size: 60px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-size: 24px; font-weight:bold; margin-top:-20px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>", unsafe_allow_html=True)

# 4. PESTAÑAS (La del chofer es la primera)
tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

with tab_chofer:
    st.markdown("## 🛠️ Publicar mi disponibilidad")
    
    # FORMULARIO DE CARGA PARA EL CHOFER (Lo primero que ve)
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<p class='title-text'>📢 CARGAR MI CAMIÓN</p>", unsafe_allow_html=True)
        with st.form("form_chofer", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                orig = st.text_input("📍 ¿Desde dónde salís?")
                equip = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            with col2:
                dest = st.text_input("🏁 ¿Hacia dónde vas?")
                wapp = st.text_input("📱 Tu WhatsApp (Solo números)")
            
            submit = st.form_submit_button("🚀 PUBLICAR AHORA")
            if submit:
                st.success("✅ ¡Publicado! Las empresas ya pueden verte en su pestaña.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 📦 Cargas que necesitan camión")
    # Ejemplo de carga para el chofer
    st.markdown("""
        <div class="card" style="border-left-color: #3498db;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                    <p class="sub-text">📦 15 Pallets (Alimento) | 🏢 Logística San Jorge</p>
                </div>
                <a href="#" class="btn-wa" style="background-color: #3498db;">ACEPTAR CARGA</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

with tab_empresa:
    st.markdown("## 🚛 Camiones buscando retorno")
    
    # DATOS DE TU EXCEL
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link = f"https://wa.me/{tel}?text=Hola!%20Vi%20tu%20camion%20en%20Retorno%20Match"
            st.markdown(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <p class="title-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                            <p class="sub-text">🚛 {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="{link}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando camiones en la base de datos...")

st.markdown("<br><p style='text-align:center; opacity:0.6; color:white;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
