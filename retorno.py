import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Hoja 6
GID_CARGAS = "1267917528"    # Hoja 5
ADMIN_PASSWORD = "1323" 

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab-list"] { display: flex; width: 100%; gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border: 2px solid white !important; }
    .card-white {
        background: white !important; border-radius: 20px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 12px solid #3498db; box-shadow: 0 10px 20px rgba(0,0,0,0.4); color: #333;
    }
    .route-style { font-size: 20px; font-weight: 900; color: #1e3799 !important; margin: 0; }
    .label-style { background: #f1f2f6; padding: 6px 12px; border-radius: 8px; font-size: 13px; color: #333; border: 1px solid #ddd; display: flex; align-items: center; gap: 5px; }
    .btn-tomar { background-color: #3498db; color: white !important; padding: 12px 20px; border-radius: 12px; text-decoration: none; font-weight: 900; }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BOTÓN DE ACTUALIZACIÓN MANUAL ---
if st.button("🔄 ACTUALIZAR DATOS AHORA"):
    st.cache_data.clear()
    st.rerun()

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_orig = st.text_input("🔍 ORIGEN (Borrar para ver todos):").strip()
with c2: b_dest = st.text_input("🏁 DESTINO (Borrar para ver todos):").strip()

tab1, tab2 = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# === PESTAÑA 1: CHOFERES (Ven cargas de Hoja 5) ===
with tab1:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1"):
            o, d, e, w = st.text_input("Origen"), st.text_input("Destino"), st.selectbox("Equipo", ["Chasis", "Semi", "Sider", "Acoplado"]), st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("✅ Publicado. Andá a 'SOY EMPRESA' para verlo."); time.sleep(1); st.rerun()
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            # Forzar descarga fresca del Excel
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            for _, r in df_c.iloc[::-1].iterrows():
                if b_orig and b_orig.lower() not in str(r[1]).lower(): continue
                if b_dest and b_dest.lower() not in str(r[2]).lower(): continue
                
                txt = urllib.parse.quote(f"Hola! Vi tu carga de {r[1]} a {r[2]} en Retorno Match. ¿Sigue disponible?")
                st.markdown(f"""
                    <div class="card-white">
                        <div>
                            <p class="route-style">📍 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</p>
                            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">
                                <div class="label-style">🏢 <b>Empresa:</b> {r[5]}</div>
                                <div class="label-style">📦 <b>Carga:</b> {r[3]}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt}" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# === PESTAÑA 2: EMPRESAS (Ven camiones de Hoja 6) ===
with tab2:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar mi Carga")
        with st.form("f2"):
            eo, ed, em, en, ew = st.text_input("Retiro"), st.text_input("Entrega"), st.text_input("Carga"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[5]:en, ID_EM[3]:ew, ID_EM[4]:"Hoy"})
                st.success("✅ Carga subida"); time.sleep(1); st.rerun()
    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            # Forzar descarga fresca del Excel
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in df_h.iloc[::-1].iterrows():
                # B=1:Origen, C=2:Destino, D=3:Equipo, E=4:Tel
                if b_orig and b_orig.lower() not in str(r[1]).lower(): continue
                if b_dest and b_dest.lower() not in str(r[2]).lower(): continue
                
                txt_h = urllib.parse.quote(f"Hola! Vi tu camión disponible de {r[1]} a {r[2]} en Retorno Match.")
                st.markdown(f"""
                    <div class="card-white" style="border-left-color: #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</p>
                            <div style="display:flex; gap:10px; margin-top:10px;">
                                <div class="label-style">⚙️ <b>Equipo:</b> {r[3]}</div>
                                <div class="label-style">📱 <b>Tel:</b> {r[4]}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_h}" class="btn-tomar" style="background:#2ecc71">CONTACTAR</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones...")

# --- PANEL ADMIN (1323) ---
with st.expander("🔐 PANEL ADMIN"):
    if st.text_input("Clave:", type="password") == ADMIN_PASSWORD:
        st.write("Fila 2 en adelante en el Excel:")
        df_admin = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
        st.dataframe(df_admin)

st.markdown("<p style='text-align:center; opacity:0.5; font-size:12px;'>© 2026 RETORNO MATCH</p>", unsafe_allow_html=True)
