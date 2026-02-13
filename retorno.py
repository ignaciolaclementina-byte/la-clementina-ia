import streamlit as st
import pandas as pd
import time
import requests

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# URL y Entry IDs del Formulario CHOFER
FORM_CHOFER_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH_ORIGEN = "entry.1304806144"
ID_CH_DESTINO = "entry.1519265625"
ID_CH_EQUIPO = "entry.597193898"
ID_CH_TEL = "entry.1574172378"

# URL y Entry IDs del Formulario EMPRESA
FORM_EMPRESA_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM_ORIGEN = "entry.610070407"
ID_EM_DESTINO = "entry.170847116"
ID_EM_MERC = "entry.576675281"
ID_EM_TEL = "entry.466540450"

# --- 2. CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    .card-container {
        background: white !important;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 14px; color: #555 !important; margin: 4px 0 0 0; }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
    }
    .stForm {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def enviar_a_google(url, payload):
    try:
        requests.post(url, data=payload, headers={'User-Agent': 'Mozilla/5.0'})
        return True
    except: return False

st.markdown("<div style='text-align:center;'><h1 style='font-size: 48px;'>🚛 RETORNO MATCH</h1><p style='color: #25D366 !important; font-weight: bold;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ==========================================
# PESTAÑA 1: VISTA CHOFER
# ==========================================
with tab1:
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_chofer", clear_on_submit=True):
            orig = st.text_input("📍 Origen")
            dest = st.text_input("🏁 Destino")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"])
            tel = st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if orig and dest and tel:
                    payload = {ID_CH_ORIGEN: orig, ID_CH_DESTINO: dest, ID_CH_EQUIPO: equi, ID_CH_TEL: tel}
                    if enviar_a_google(FORM_CHOFER_URL, payload):
                        st.success("✅ ¡Publicado!")
                        time.sleep(1.5)
                        st.rerun()

    with col_f2:
        st.markdown("### 📦 Cargas Disponibles")
        URL_CARGAS_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
        try:
            df_c = pd.read_csv(URL_CARGAS_CSV)
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            if not df_c.empty:
                for _, row in df_c.iloc[::-1].head(15).iterrows():
                    # --- LÓGICA WHATSAPP CHOFER ---
                    tel_raw = str(row['tel']).strip()
                    tel_clean = "".join(filter(str.isdigit, tel_raw))
                    if tel_clean.startswith('0'): tel_clean = tel_clean[1:]
                    tel_final = tel_clean if tel_clean.startswith('549') else "549" + tel_clean
                    
                    st.markdown(f"""
                        <div class="card-container" style="border-left: 8px solid #3498db;">
                            <div style="flex-grow:1;">
                                <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                                <p class="detail-text">📦 <b>Carga:</b> {row['mercaderia']} | 📅 {row['fecha']}</p>
                            </div>
                            <a href="https://wa.me/{tel_final}" target="_blank" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Cargando base de datos...")

# ==========================================
# PESTAÑA 2: VISTA EMPRESA
# ==========================================
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    
    with col_e1:
        st.markdown("### 📢 Publicar Nueva Carga")
        with st.form("form_empresa", clear_on_submit=True):
            e_orig = st.text_input("📍 Punto de Retiro")
            e_dest = st.text_input("🏁 Punto de Entrega")
            e_merc = st.text_input("📦 Mercadería")
            e_tel = st.text_input("📱 WhatsApp Contacto")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if e_orig and e_dest and e_tel:
                    p_e = {ID_EM_ORIGEN: e_orig, ID_EM_DESTINO: e_dest, ID_EM_MERC: e_merc, ID_EM_TEL: e_tel}
                    if enviar_a_google(FORM_EMPRESA_URL, p_e):
                        st.success("✅ ¡Carga en línea!")
                        time.sleep(1.5)
                        st.rerun()

    with col_e2:
        st.markdown("### 🚛 Camiones Disponibles")
        URL_CHOFERES_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
        try:
            df_h = pd.read_csv(URL_CHOFERES_CSV)
            df_h.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            if not df_h.empty:
                for _, row in df_h.iloc[::-1].head(15).iterrows():
                    # --- LÓGICA WHATSAPP EMPRESA ---
                    tel_raw = str(row['tel']).strip()
                    tel_clean = "".join(filter(str.isdigit, tel_raw))
                    if tel_clean.startswith('0'): tel_clean = tel_clean[1:]
                    tel_final = tel_clean if tel_clean.startswith('549') else "549" + tel_clean
                    
                    st.markdown(f"""
                        <div class="card-container" style="border-left: 8px solid #25D366;">
                            <div style="flex-grow:1;">
                                <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                                <p class="detail-text">🚛 <b>Equipo:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                            </div>
                            <a href="https://wa.me/{tel_final}" target="_blank" class="btn-wa">WHATSAPP</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Sincronizando camiones...")
