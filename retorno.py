import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN EXACTA (EXTRAÍDA DE TUS ENLACES) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Hoja 6 (Camiones)
GID_CARGAS = "1267917528"    # Hoja 5 (Cargas)
ADMIN_PASSWORD = "1323" 

# URLS DE ENVÍO CORREGIDAS
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. DISEÑO ADAPTADO A CELULAR ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab-list"] { display: flex; gap: 5px; width: 100%; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 10px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important; border: 1px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    
    .card-white {
        background: white !important; border-radius: 15px; padding: 15px; margin-bottom: 12px;
        border-left: 10px solid #3498db; color: #333;
    }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; margin-bottom: 5px; }
    .info-tag { 
        background: #f1f2f6; padding: 4px 8px; border-radius: 6px; font-size: 13px; 
        color: #555; border: 1px solid #ddd; margin-right: 5px; display: inline-block;
    }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 10px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_origen = st.text_input("🔍 ORIGEN (Ciudad):").strip()
with c2: b_destino = st.text_input("🏁 DESTINO (Ciudad):").strip()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA CHOFERES (Ven cargas / Publican Camión)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2])
    with col_i:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            orig = st.text_input("📍 Mi Ubicación")
            dest = st.text_input("🏁 Destino deseado")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Térmico"])
            wsp = st.text_input("📱 Mi WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                # IDs de tu Formulario de Camiones
                data_ch = {
                    "entry.1304806144": orig,
                    "entry.1519265625": dest,
                    "entry.597193898": equi,
                    "entry.1574172378": wsp
                }
                requests.post(URL_CHOFERES_POST, data=data_ch)
                st.success("✅ ¡Listo! Aparecerás en la pestaña EMPRESAS.")
                time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            url_cargas = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
            df_c = pd.read_csv(url_cargas).fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                # Col B: Retiro, C: Entrega, D: Carga, E: WhatsApp, F: Empresa, G: Cuándo
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                txt = urllib.parse.quote(f"Hola! Vi tu carga de {r[1]} a {r[2]} en Retorno Match.")
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <span class="info-tag">🏢 {r[5]}</span> <span class="info-tag">📦 {r[3]}</span> <span class="info-tag">⏳ {r[6]}</span>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt}" class="btn-wsp">TOMAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Cargando datos...")

# ==========================================
# PESTAÑA EMPRESAS (Ven camiones / Publican Carga)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_em", clear_on_submit=True):
            e_o = st.text_input("📍 Origen")
            e_d = st.text_input("🏁 Destino")
            e_c = st.text_input("📦 Carga")
            e_n = st.text_input("🏢 Empresa")
            e_u = st.selectbox("⏳ Cuándo", ["Sale hoy", "Sale mañana", "A convenir"])
            e_w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                # IDs de tu Formulario de Cargas
                data_em = {
                    "entry.610070407": e_o,
                    "entry.170847116": e_d,
                    "entry.576675281": e_c,
                    "entry.1930562861": e_n,
                    "entry.1064058502": e_u,
                    "entry.466540450": e_w
                }
                requests.post(URL_CARGAS_POST, data=data_em)
                st.success("✅ Carga en línea."); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
            df_h = pd.read_csv(url_ch).fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                
                txt_h = urllib.parse.quote(f"Hola! Vi tu camión de {r[1]} a {r[2]} en Retorno Match.")
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #2ecc71;">
                    <div class="route-txt">🚛 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <span class="info-tag">⚙️ {r[3]}</span> <span class="info-tag">📱 {r[4]}</span>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_h}" class="btn-wsp" style="background:#2c3e50">HABLAR CON CHOFER</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones...")

# --- PANEL ADMIN ---
with st.expander("🔐 PANEL ADMIN (1323)"):
    if st.text_input("Clave", type="password") == ADMIN_PASSWORD:
        st.write("Identificá la fila en el Excel para borrar:")
        adm_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}")
        st.dataframe(adm_c.tail(5))

st.markdown("<center><small>© 2026 RETORNO MATCH</small></center>", unsafe_allow_html=True)
