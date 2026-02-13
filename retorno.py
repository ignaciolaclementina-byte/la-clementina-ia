import streamlit as st
import pandas as pd
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS "NUCLEAR" PARA PERFORAR EL FONDO NEGRO
st.markdown("""
    <style>
    /* 1. FORZAR LA IMAGEN EN LA CAPA MÁS PROFUNDA */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                          url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* 2. MATAR EL COLOR NEGRO DE TODOS LOS CONTENEDORES DE STREAMLIT */
    .stApp, .stMain, [data-testid="stHeader"], [data-testid="stAppViewMain"], .main, .block-container {
        background: transparent !important;
        background-color: transparent !important;
    }

    /* 3. TARJETAS PROFESIONALES (Blanco limpio con sombra) */
    .card {
        background-color: white !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border-left: 8px solid #25D366;
    }

    /* 4. TÍTULOS Y TEXTOS */
    h1, h2, h3, label, .stMarkdown p {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }
    
    /* Texto negro dentro de las tarjetas */
    .card p, .card h3 {
        color: #1a1a1a !important;
        text-shadow: none !important;
        margin: 5px 0;
    }

    /* 5. DISEÑO DE PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #25D366 !important;
        border-radius: 8px;
    }

    /* 6. BOTONES */
    .btn-action {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO LIMPIO
st.markdown("<h1 style='text-align:center; font-size: 55px; margin-bottom:0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366 !important; font-size: 20px; font-weight:bold; margin-top:-10px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>", unsafe_allow_html=True)

# 4. SISTEMA DE PESTAÑAS
tab1, tab2 = st.tabs(["🚀 PARA CHOFERES (Busco Carga)", "🏢 PARA EMPRESAS (Busco Camión)"])

# --- VISTA CHOFER ---
with tab1:
    st.markdown("### 🛠️ Herramientas del Transportista")
    
    # Formulario simplificado dentro de una tarjeta
    with st.container():
        st.markdown('<div class="card" style="border-left-color: #3498db;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#3498db !important;'>📢 PUBLICAR MI DISPONIBILIDAD</h3>", unsafe_allow_html=True)
        with st.form("f_chofer", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                orig = st.text_input("📍 Origen")
                equip = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            with c2:
                dest = st.text_input("🏁 Destino")
                wapp = st.text_input("📱 WhatsApp (Sin espacios)")
            
            if st.form_submit_button("PUBLICAR AHORA"):
                st.success("¡Publicado con éxito!")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### 📦 Cargas Disponibles")
    # Ejemplo de carga
    st.markdown("""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3 style="margin:0;">📍 ROSARIO → SAN JORGE</h3>
                    <p><b>Mercadería:</b> 12 Pallets | <b>Empresa:</b> Distribuidora S.J.</p>
                </div>
                <a href="#" class="btn-action">ACEPTAR VIAJE</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- VISTA EMPRESA ---
with tab2:
    st.markdown("### 🚛 Camiones buscando retorno")
    
    # LECTURA DE GOOGLE SHEETS
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
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin:0;">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</h3>
                            <p><b>Equipo:</b> {row['equipo']} | <b>Publicado:</b> {row['fecha']}</p>
                        </div>
                        <a href="{link}" target="_blank" class="btn-action">WHATSAPP</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Sincronizando con la base de datos de camiones...")

st.markdown("<br><p style='text-align:center; opacity:0.5; color:white;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
