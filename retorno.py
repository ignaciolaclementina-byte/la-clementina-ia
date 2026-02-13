import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# URLS DE FORMULARIOS
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
# Usando los IDs que pasaste en el link
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.466540450"]

# --- 2. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    .card-container {
        background: white !important; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .company-tag { background: #e8f0fe; padding: 3px 10px; border-radius: 6px; color: #1967d2; font-weight: bold; font-size: 13px; border: 1px solid #1967d2; }
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 22px; border-radius: 50px; text-decoration: none; font-weight: bold; }
    .stForm { background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 15px !important; padding: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_solo_hoy(df):
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= hace_24hs].copy()
    except: return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 48px;'>🚛 RETORNO MATCH</h1><p style='color: #25D366 !important; font-weight: bold;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ================= VISTA CHOFER (Busca Carga) =================
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o, d = st.text_input("📍 Origen"), st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"])
            t = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if o and d and t:
                    requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:t})
                    st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 📦 Cargas Disponibles (Últimas 24hs)")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c = filtrar_solo_hoy(df_c)
            if df_c.empty:
                st.info("No hay cargas nuevas de hoy.")
            else:
                for _, row in df_c.iloc[::-1].iterrows():
                    # Columnas: Fecha(0), Retiro(1), Entrega(2), Mercadería(3), Empresa(4), Tel(5)
                    f, ori, des, mer, emp, tel = row[0], row[1], row[2], row[3], row[4], row[5]
                    t_clean = "".join(filter(str.isdigit, str(tel)))
                    t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                    msg = urllib.parse.quote(f"Hola! Vi tu carga en Retorno Match: {ori} -> {des} ({mer}). Sigue disponible?")
                    
                    st.markdown(f"""
                        <div class="card-container" style="border-left: 8px solid #3498db;">
                            <div style="flex-grow:1;">
                                <p class="route-text">📍 {str(ori).upper()} ➔ {str(des).upper()}</p>
                                <p class="detail-text" style="color:#555; margin-bottom:8px;">📦 {mer} | <span class="company-tag">🏢 {emp}</span></p>
                                <p style="color:gray; font-size:12px;">🕒 Publicado: {f.strftime('%H:%M hs')}</p>
                            </div>
                            <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Sincronizando con el servidor...")

# ================= VISTA EMPRESA (Busca Camión) =================
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 🏢 Publicar Nueva Carga")
        with st.form("f_em", clear_on_submit=True):
            eo, ed = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega")
            em = st.text_input("📦 Mercadería")
            en = st.text_input("🏢 Nombre de Empresa")
            et = st.text_input("📱 WhatsApp de Contacto")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if eo and ed and en and et:
                    requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:et})
                    st.success("✅ ¡Carga en línea!"); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 🚛 Camiones Disponibles (Últimas 24hs)")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            df_h = filtrar_solo_hoy(df_h)
            if df_h.empty:
                st.info("No hay camiones disponibles de hoy.")
            else:
                for _, row in df_h.iloc[::-1].iterrows():
                    f, ori, des, eq, tel = row[0], row[1], row[2], row[3], row[4]
                    t_clean = "".join(filter(str.isdigit, str(tel)))
                    t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                    msg_ch = urllib.parse.quote(f"Hola! Vi tu camión en Retorno Match: {ori} -> {des} ({eq}). Te interesa una carga?")
                    
                    st.markdown(f"""
                        <div class="card-container" style="border-left: 8px solid #25D366;">
                            <div style="flex-grow:1;">
                                <p class="route-text">📍 {str(ori).upper()} ➔ {str(des).upper()}</p>
                                <p class="detail-text" style="color:#555;">🚛 Equipo: {eq} | 🕒 {f.strftime('%H:%M hs')}</p>
                            </div>
                            <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg_ch}" target="_blank" class="btn-wa">WHATSAPP</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Actualizando lista...")
