import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. LÓGICA ---
def obtener_color_urgencia(estado):
    est = str(estado).lower()
    if "hoy" in est: return "#FF4B4B"
    if "mañana" in est: return "#F1C40F"
    return "#3498DB"

# --- 3. INTERFAZ Y ESTILOS (RESPETANDO TU DISEÑO) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    
    /* PESTAÑAS MÁS GRANDES Y CLARAS */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 60px; background-color: rgba(255,255,255,0.1); border-radius: 10px 10px 0 0;
        padding: 0 30px; font-size: 20px !important; font-weight: 800 !important; color: white !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border-bottom: 4px solid white !important; }

    /* TARJETAS */
    .card-white {
        background: white !important; border-radius: 15px; padding: 18px; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center; border-left: 10px solid #3498db;
    }
    
    @media (max-width: 640px) {
        .card-white { flex-direction: column; align-items: flex-start; gap: 10px; }
        .btn-tomar { width: 100%; text-align: center; }
    }

    .route-style { font-size: 19px; font-weight: 900; color: #1e3799 !important; margin: 0 0 10px 0; }
    
    .label-style { 
        background: #f1f2f6; padding: 6px 12px; border-radius: 8px; font-size: 14px; 
        color: #2f3542; border: 1px solid #dcdde1; display: flex; align-items: center; gap: 5px; margin-bottom: 5px;
    }
    .label-style b { color: #1e3799; font-weight: 800; }

    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 14px 25px; 
        border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 15px;
    }
    
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h1 style='font-size: 45px; font-weight: 900;'>🚛 RETORNO MATCH</h1></div>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2 = st.columns(2)
with c_b1: b_orig = st.text_input("🔍 Buscar Origen:")
with c_b2: b_dest = st.text_input("🔍 Buscar Destino:")

# PESTAÑAS CLARAS
t1, t2 = st.tabs(["🚀 SOY CHOFER (Ver Cargas)", "🏢 SOY EMPRESA (Ver Camiones)"])

# === PESTAÑA 1: CHOFERES ===
with t1:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o, d, e, w = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Térmico"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            for _, r in df.iloc[::-1].iterrows():
                # Mapeo: 1:Ret, 2:Ent, 3:Merc, 4:Tel, 5:Emp, 6:Urg
                ret, ent, mer, tel, emp, urg = r[1], r[2], r[3], r[4], r[5], r[6]
                
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                color_u = obtener_color_urgencia(urg)
                txt_ws = urllib.parse.quote(f"Hola! Vi tu carga de {ret} a {ent} ({mer}) en Retorno Match. ¿Sigue disponible?")
                
                st.markdown(f"""
                    <div class="card-white" style="border-left-color: {color_u};">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                                <div class="label-style">🏢 <b>Empresa:</b> {emp}</div>
                                <div class="label-style">📦 <b>Carga:</b> {mer}</div>
                                <div class="label-style">⏳ <b>Sale:</b> {urg}</div>
                                <div class="label-style">📱 <b>Tel:</b> {tel}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone=549{tel}&text={txt_ws}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Conectando con base de datos...")

# === PESTAÑA 2: EMPRESAS ===
with t2:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar mi Carga")
        with st.form("f2", clear_on_submit=True):
            eo, ed, em, en = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega"), st.text_input("📦 Carga"), st.text_input("🏢 Empresa")
            eu, ew = st.selectbox("⏳ ¿Cuándo?", ["Sale hoy", "Sale mañana", "Sin apuro"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[5]:en, ID_EM[3]:ew, ID_EM[4]:eu})
                st.success("¡Carga publicada!"); time.sleep(1); st.rerun()
    
    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in dfh.iloc[::-1].iterrows():
                o_h, d_h, eq_h, tel_h = r[1], r[2], r[3], r[4]
                st.markdown(f"""
                    <div class="card-white" style="border-left-color: #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(o_h).upper()} ➔ {str(d_h).upper()}</p>
                            <div style="display: flex; gap: 10px;">
                                <div class="label-style">⚙️ <b>Equipo:</b> {eq_h}</div>
                                <div class="label-style">📱 <b>Tel:</b> {tel_h}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone=549{tel_h}" target="_blank" class="btn-tomar" style="background:#2ecc71">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

st.markdown("<br><hr><p style='text-align:center; opacity:0.6; font-size:12px;'>© 2026 RETORNO MATCH - Ignacio Diaz | San Jorge</p>", unsafe_allow_html=True)
