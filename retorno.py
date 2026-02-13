import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. CSS "BLINDADO" (Para que el fondo no se pierda y sea profesional)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }
    .stApp, .stMain, [data-testid="stHeader"], .block-container { background: transparent !important; }

    /* Tarjetas */
    .card {
        background: white !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        color: #1a1a1a !important;
    }
    .card-title { font-size: 20px; font-weight: bold; margin: 0; color: #1a1a1a !important; }
    .card-sub { font-size: 16px; color: #444 !important; margin: 5px 0; }

    /* Botones */
    .btn {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        color: white !important;
    }
    .btn-green { background-color: #25D366; }
    .btn-blue { background-color: #3498db; }

    /* Estilo de Pestañas */
    .stTabs [data-baseweb="tab-list"] { background-color: rgba(255,255,255,0.1); border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; }
    .stTabs [aria-selected="true"] { background-color: #25D366 !important; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATOS DE CONEXIÓN
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# URL para Camiones (Hoja 3)
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
# URL para Cargas (Deberías crear una hoja llamada 'Cargas' en el mismo Excel)
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Cargas&t={int(time.time())}"

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- VISTA CHOFER (Busca lo que las empresas publicaron) ---
with tab_chofer:
    st.markdown("### 📦 Cargas Disponibles")
    
    # Intentamos leer las cargas de la hoja de Excel
    try:
        df_cargas = pd.read_csv(URL_CARGAS).iloc[:, :5]
        df_cargas.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
        
        for _, row in df_cargas.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link = f"https://wa.me/{tel}?text=Hola!%20Me%20interesa%20la%20carga%20de%20{row['origen']}"
            st.markdown(f"""
                <div class="card" style="border-left: 8px solid #3498db;">
                    <p class="card-title">📍 {row['origen'].upper()} → {row['destino'].upper()}</p>
                    <p class="card-sub">📦 <b>CARGA:</b> {row['mercaderia']}</p>
                    <a href="{link}" target="_blank" class="btn btn-blue">ACEPTAR VIAJE</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Aún no hay cargas publicadas por empresas o la hoja 'Cargas' no existe.")

# --- VISTA EMPRESA (Publica carga y busca camiones) ---
with tab_empresa:
    with st.expander("📢 PUBLICAR NUEVA CARGA"):
        with st.form("form_carga"):
            st.write("Complete los datos para que los choferes lo contacten:")
            e_orig = st.text_input("Origen")
            e_dest = st.text_input("Destino")
            e_merc = st.text_input("Mercadería")
            e_tel = st.text_input("WhatsApp de contacto")
            
            if st.form_submit_button("PUBLICAR CARGA"):
                # Aquí deberías poner el URL de un SEGUNDO Google Form para guardar las cargas
                st.success("✅ Carga enviada. (Recordá conectar esto a tu Google Form de Cargas)")

    st.markdown("### 🚛 Camiones Disponibles")
    try:
        df_camiones = pd.read_csv(URL_CAMIONES).iloc[:, :5]
        df_camiones.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        for _, row in df_camiones.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            st.markdown(f"""
                <div class="card" style="border-left: 8px solid #25D366;">
                    <p class="card-title">📍 {row['origen'].upper()} → {row['destino'].upper()}</p>
                    <p class="card-sub">🚛 <b>EQUIPO:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                    <a href="https://wa.me/{tel}" target="_blank" class="btn btn-green">WHATSAPP</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("Buscando camiones...")
