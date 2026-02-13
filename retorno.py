import streamlit as st
import pandas as pd
import time
import requests

# --- 1. CONFIGURACIÓN TÉCNICA (PEGÁ TUS IDS ACÁ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs" # Cambialo si creaste uno nuevo
GID_CHOFERES = "0"          # Reemplazá con el GID de la hoja de camiones
GID_CARGAS = "123456789"    # Reemplazá con el GID de la hoja de cargas

# IDs de Formulario Chofer
FORM_CHOFER_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH_ORIGEN = "entry.1304806144"
ID_CH_DESTINO = "entry.1519265625"
ID_CH_EQUIPO = "entry.597193898"
ID_CH_TEL = "entry.1574172378"

# IDs de Formulario Empresa
FORM_EMPRESA_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM_ORIGEN = "entry.610070407"
ID_EM_DESTINO = "entry.170847116"
ID_EM_MERC = "entry.576675281"
ID_EM_TEL = "entry.466540450"

# --- 2. INTERFAZ Y ESTILO ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
    }
    .stApp { background: transparent !important; }
    .card-container {
        background: white !important; border-radius: 12px; padding: 15px; margin-bottom: 10px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .route-text { font-size: 18px; font-weight: bold; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 13px; color: #666 !important; margin: 0; }
    .btn-wa { background-color: #25D366; color: white !important; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- FUNCIONES DE CARGA ---
def enviar_datos(url, payload):
    try:
        requests.post(url, data=payload)
        return True
    except: return False

# --- VISTA CHOFER ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o = st.text_input("📍 Origen")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            t = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                pay = {ID_CH_ORIGEN: o, ID_CH_DESTINO: d, ID_CH_EQUIPO: e, ID_CH_TEL: t}
                if enviar_datos(FORM_CHOFER_URL, pay):
                    st.success("✅ ¡Publicado! Las empresas ya pueden verte.")
                    time.sleep(1)
                    st.rerun()

    with col2:
        st.subheader("📦 Cargas disponibles")
        URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
        try:
            df_c = pd.read_csv(URL_CARGAS)
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            for _, row in df_c.iloc[::-1].head(10).iterrows():
                st.markdown(f'<div class="card-container" style="border-left: 8px solid #3498db;"><div><p class="route-text">📍 {row["origen"].upper()} ➔ {row["destino"].upper()}</p><p class="detail-text">📦 {row["mercaderia"]} | 📅 {row["fecha"]}</p></div><a href="https://wa.me/{row["tel"]}" target="_blank" class="btn-wa" style="background-color:#3498db;">TOMAR CARGA</a></div>', unsafe_allow_html=True)
        except: st.info("Buscando nuevas cargas de empresas...")

# --- VISTA EMPRESA ---
with tab2:
    col3, col4 = st.columns([1, 2])
    with col3:
        st.subheader("📢 Publicar Carga")
        with st.form("f_em", clear_on_submit=True):
            eo = st.text_input("📍 Punto de Retiro")
            ed = st.text_input("🏁 Punto de Entrega")
            em = st.text_input("📦 Mercadería")
            et = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("BUSCAR CAMIÓN AHORA", use_container_width=True):
                pay_e = {ID_EM_ORIGEN: eo, ID_EM_DESTINO: ed, ID_EM_MERC: em, ID_EM_TEL: et}
                if enviar_datos(FORM_EMPRESA_URL, pay_e):
                    st.success("✅ ¡Carga publicada!")
                    time.sleep(1)
                    st.rerun()

    with col4:
        st.subheader("🚛 Camiones disponibles")
        URL_CHOF = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
        try:
            df_h = pd.read_csv(URL_CHOF)
            df_h.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            for _, row in df_h.iloc[::-1].head(10).iterrows():
                st.markdown(f'<div class="card-container" style="border-left: 8px solid #25D366;"><div><p class="route-text">📍 {row["origen"].upper()} ➔ {row["destino"].upper()}</p><p class="detail-text">🚛 {row["equipo"]} | 📅 {row["fecha"]}</p></div><a href="https://wa.me/{row["tel"]}" target="_blank" class="btn-wa">WHATSAPP</a></div>', unsafe_allow_html=True)
        except: st.info("Buscando camiones disponibles...")
