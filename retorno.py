import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.466540450"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. NUEVO DISEÑO DE TARJETAS (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    
    /* Contenedor principal de la tarjeta */
    .card {
        background: white !important;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        border-left: 10px solid #3498db; /* Azul para cargas */
    }
    .card-truck { border-left: 10px solid #25D366; } /* Verde para camiones */

    /* Sección de textos */
    .card-info { flex-grow: 1; }
    .route-header { 
        font-size: 22px; 
        font-weight: 900; 
        color: #2c3e50 !important; 
        margin: 0 0 10px 0;
        display: flex;
        align-items: center;
    }
    .details-row {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
        font-size: 15px;
        color: #555 !important;
    }
    .detail-item {
        background: #f8f9fa;
        padding: 5px 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
        border: 1px solid #eee;
    }
    
    /* Botón lateral */
    .btn-side {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        transition: 0.3s;
        text-align: center;
        min-width: 140px;
    }
    .btn-side:hover { transform: scale(1.05); background-color: #128C7E; }
    
    .stForm { background: rgba(255, 255, 255, 0.08) !important; border-radius: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_solo_hoy(df):
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= hace_24hs].copy()
    except: return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 50px;'>🚛 RETORNO MATCH</h1><p style='color: #25D366; font-weight: bold; font-size: 20px;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ================= VISTA CHOFER (Busca Carga) =================
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 📢 Publicar Camión")
        with st.form("f_ch", clear_on_submit=True):
            o, d = st.text_input("📍 Origen"), st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"])
            t = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if o and d and t:
                    requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:t})
                    st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c = filtrar_solo_hoy(df_c)
            if df_c.empty:
                st.info("No hay cargas registradas hoy.")
            else:
                for _, row in df_c.iloc[::-1].iterrows():
                    f, ori, des, mer, emp, tel = row[0], row[1], row[2], row[3], row[4], row[5]
                    t_clean = "".join(filter(str.isdigit, str(tel)))
                    t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                    msg = urllib.parse.quote(f"Hola! Vi tu carga en Retorno Match: {ori} -> {des}.")
                    
                    st.markdown(f"""
                        <div class="card">
                            <div class="card-info">
                                <p class="route-header">📍 {str(ori).upper()} ➔ {str(des).upper()}</p>
                                <div class="details-row">
                                    <span class="detail-item">📦 <b>Carga:</b> {mer}</span>
                                    <span class="detail-item">🏢 <b>Empresa:</b> {emp}</span>
                                    <span class="detail-item">🕒 {f.strftime('%H:%M hs')}</span>
                                </div>
                            </div>
                            <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-side" style="background-color: #3498db;">TOMAR CARGA</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# ================= VISTA EMPRESA (Busca Camión) =================
with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_em", clear_on_submit=True):
            eo, ed = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega")
            em = st.text_input("📦 Mercadería")
            en = st.text_input("🏢 Nombre de Empresa")
            et = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if eo and ed and en and et:
                    requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:et})
                    st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            df_h = filtrar_solo_hoy(df_h)
            if df_h.empty:
                st.info("No hay camiones hoy.")
            else:
                for _, row in df_h.iloc[::-1].iterrows():
                    f, ori, des, eq, tel = row[0], row[1], row[2], row[3], row[4]
                    t_clean = "".join(filter(str.isdigit, str(tel)))
                    t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                    st.markdown(f"""
                        <div class="card card-truck">
                            <div class="card-info">
                                <p class="route-header">🚛 {str(ori).upper()} ➔ {str(des).upper()}</p>
                                <div class="details-row">
                                    <span class="detail-item">⚙️ <b>Equipo:</b> {eq}</span>
                                    <span class="detail-item">🕒 {f.strftime('%H:%M hs')}</span>
                                </div>
                            </div>
                            <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-side">CONTACTAR</a>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")
