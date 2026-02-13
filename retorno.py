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

# --- 2. DISEÑO DE INTERFAZ (CSS MEJORADO) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }

    /* Estilo de Tarjetas */
    .card-pro {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        border-bottom: 5px solid #3498db;
        transition: transform 0.2s ease;
    }
    .card-pro:hover { transform: translateY(-5px); }
    .card-truck { border-bottom: 5px solid #2ecc71; }

    /* Info de Ruta */
    .route-main { 
        font-size: 24px; 
        font-weight: 900; 
        color: #1e272e !important; 
        margin-bottom: 12px;
        letter-spacing: -0.5px;
    }
    
    /* Chips de detalles */
    .detail-pill {
        display: inline-flex;
        align-items: center;
        background: #f1f2f6;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 14px;
        color: #2f3542;
        font-weight: 600;
        margin-right: 8px;
        margin-bottom: 6px;
        border: 1px solid #dfe4ea;
    }

    /* Botón WhatsApp Pro */
    .btn-action {
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white !important;
        padding: 14px 28px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: 800;
        text-transform: uppercase;
        font-size: 14px;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.4);
        transition: 0.3s;
        text-align: center;
        min-width: 150px;
    }
    .btn-wa { background: linear-gradient(135deg, #2ecc71, #27ae60); box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4); }
    .btn-action:hover { opacity: 0.9; box-shadow: 0 6px 20px rgba(0,0,0,0.2); transform: scale(1.02); }

    .stForm { background: rgba(0,0,0,0.4) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_solo_hoy(df):
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= hace_24hs].copy()
    except: return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 55px; font-weight: 900; margin-bottom:0;'>🚛 RETORNO MATCH</h1><p style='color: #2ecc71; font-size: 22px; font-weight: 700; margin-top:0;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["🚀 BUSCO CARGA (Soy Chofer)", "🏢 BUSCO CAMIÓN (Soy Empresa)"])

# ================= VISTA CHOFER =================
with tab1:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o, d = st.text_input("📍 Origen"), st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"])
            t = st.text_input("📱 WhatsApp (Ej: 3406...)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if o and d and t:
                    requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:t})
                    st.success("✅ Publicado con éxito"); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c = filtrar_solo_hoy(df_c)
            for _, row in df_c.iloc[::-1].iterrows():
                f, ori, des, mer, emp, tel = row[0], row[1], row[2], row[3], row[4], row[5]
                t_clean = "".join(filter(str.isdigit, str(tel)))
                t_final = t_clean if t_clean.startswith('54') else "549" + t_clean
                msg = urllib.parse.quote(f"Hola! Me interesa la carga: {ori} -> {des}.")
                
                st.markdown(f"""
                    <div class="card-pro">
                        <div style="flex-grow:1;">
                            <div class="route-main">📍 {str(ori).upper()} ➔ {str(des).upper()}</div>
                            <div>
                                <span class="detail-pill">📦 {mer}</span>
                                <span class="detail-pill">🏢 {emp}</span>
                                <span class="detail-pill">🕒 {f.strftime('%H:%M')} hs</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-action">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# ================= VISTA EMPRESA =================
with tab2:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_em", clear_on_submit=True):
            eo, ed = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega")
            em, en = st.text_input("📦 Mercadería"), st.text_input("🏢 Empresa")
            et = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if eo and ed and en and et:
                    requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:et})
                    st.success("✅ Carga en línea"); time.sleep(1); st.rerun()
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
                    <div class="card-pro card-truck">
                        <div style="flex-grow:1;">
                            <div class="route-main">🚛 {str(ori).upper()} ➔ {str(des).upper()}</div>
                            <div>
                                <span class="detail-pill">⚙️ {eq}</span>
                                <span class="detail-pill">🕒 {f.strftime('%H:%M')} hs</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-action btn-wa">CONTACTAR</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")
