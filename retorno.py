import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
# IDs actualizados según tu link: Origen, Destino, Mercadería, Empresa, WhatsApp
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.466540450"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- MANTENEMOS TU INTERFAZ ORIGINAL ---
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
        background: white !important; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 14px; color: #555 !important; margin: 4px 0 0 0; }
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: bold; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_solo_hoy(df):
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= hace_24hs].copy()
    except: return df

st.markdown("<div style='text-align:center;'><h1>🚛 RETORNO MATCH</h1><p>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- PESTAÑA CHOFER ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o = st.text_input("📍 Origen")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            t = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:t})
                st.success("✅ Publicado"); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c = filtrar_solo_hoy(df_c)
            for _, row in df_c.iloc[::-1].iterrows():
                # Leemos los datos de la planilla según tus columnas actuales
                f, ori, des, mer, emp, tel = row[0], row[1], row[2], row[3], row[4], row[5]
                t_clean = "".join(filter(str.isdigit, str(tel)))
                t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                msg = urllib.parse.quote(f"Hola! Me interesa la carga {ori} -> {des} de la empresa {emp}.")
                
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #3498db;">
                        <div style="flex-grow:1;">
                            <p class="route-text">📍 {str(ori).upper()} ➔ {str(des).upper()}</p>
                            <p class="detail-text">📦 {mer} | 🏢 {emp} | 🕒 {f.strftime('%H:%M')}</p>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# --- PESTAÑA EMPRESA ---
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🏢 Publicar Nueva Carga")
        with st.form("f_em", clear_on_submit=True):
            eo = st.text_input("📍 Retiro")
            ed = st.text_input("🏁 Entrega")
            em = st.text_input("📦 Mercadería")
            en = st.text_input("🏢 Nombre de Empresa") # Campo nuevo
            et = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:et})
                st.success("✅ Carga Publicada"); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            df_h = filtrar_solo_hoy(df_h)
            for _, row in df_h.iloc[::-1].iterrows():
                f, ori, des, eq, tel = row[0], row[1], row[2], row[3], row[4]
                t_clean = "".join(filter(str.isdigit, str(tel)))
                t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #25D366;">
                        <div style="flex-grow:1;">
                            <p class="route-text">🚛 {str(ori).upper()} ➔ {str(des).upper()}</p>
                            <p class="detail-text">⚙️ Equipo: {eq} | 🕒 {f.strftime('%H:%M')}</p>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")
