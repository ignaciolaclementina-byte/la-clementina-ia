import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    
ADMIN_PASSWORD = "1323" 
SCRIPT_BORRAR = "https://script.google.com/macros/s/AKfycbwtc_n-zJL-yS-3wpQAXW6mYOALNb19vsiOYCDBWbc-tWsiSCdSh1_AC-3Mon--vZ3E/exec"

# URLS DE FORMULARIOS
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- FUNCIÓN DE CARGA ULTRA RÁPIDA ---
@st.cache_data(ttl=5) # Cache de solo 5 segundos
def get_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&t={int(time.time())}"
    return pd.read_csv(url).fillna("-")

# --- 2. DISEÑO ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 60px !important; background-color: #2c3e50 !important;
        border-radius: 10px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 12px; padding: 12px; margin-bottom: 10px;
        border-left: 8px solid #3498db; color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .route-txt { font-size: 18px; font-weight: 900; color: #1e3799; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 8px; 
        border-radius: 6px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 8px;
    }
    /* Estilo para el botón de actualizar */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #3498db;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES Y BOTÓN ACTUALIZAR ---
col_busc1, col_busc2, col_refresh = st.columns([2, 2, 1])

with col_busc1: 
    b_origen = st.text_input("🔍 ORIGEN:").strip()
with col_busc2: 
    b_destino = st.text_input("🏁 DESTINO:").strip()
with col_refresh:
    st.write("<br>", unsafe_allow_html=True) # Espaciador para alinear con inputs
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve Cargas)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2])
    with col_i:
        st.markdown("### 📢 Publicar Camión")
        with st.form("f_chofer", clear_on_submit=True):
            ch_o, ch_d = st.text_input("📍 Ubicación"), st.text_input("🏁 Destino")
            ch_e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea"])
            ch_w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": ch_o, "entry.1519265625": ch_d, "entry.597193898": ch_e, "entry.1574172378": ch_w})
                st.cache_data.clear()
                st.success("✅ Publicado")
                st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = get_data(GID_CARGAS)
            for i, r in df_c.iloc[::-1].iterrows(): 
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                txt = urllib.parse.quote(f"*RETORNO MATCH*\nMe interesa la carga: {r[1]} -> {r[2]}")
                st.markdown(f"""<div class="card-white">
                    <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                    <b>📦 {r[3]}</b> | 🏢 {r[5]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt}" target="_blank" class="btn-wsp">CONTACTAR</a>
                </div>""", unsafe_allow_html=True)
                
                with st.expander(f"⚙️ Borrar Fila {i+2}"):
                    if st.text_input(f"Psw {i}", type="password", key=f"p_c_{i}") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar", key=f"b_c_{i}"):
                            requests.get(f"{SCRIPT_BORRAR}?gid={GID_CARGAS}&fila={i+2}")
                            st.cache_data.clear()
                            st.rerun()
        except: st.warning("Conectando con Google...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve Camiones)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_empresa", clear_on_submit=True):
            em_o, em_d, em_c, em_n, em_w = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega"), st.text_input("📦 Carga"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": em_o, "entry.170847116": em_d, "entry.576675281": em_c, "entry.1930562861": em_n, "entry.466540450": em_w})
                st.cache_data.clear()
                st.success("✅ Subida")
                st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = get_data(GID_CHOFERES)
            for i, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                txt_h = urllib.parse.quote(f"*RETORNO MATCH*\nVi tu camión en {r[1]}")
                st.markdown(f"""<div class="card-white" style="border-left-color:#2ecc71">
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <b>⚙️ {r[3]}</b> | 📱 {r[4]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_h}" target="_blank" class="btn-wsp" style="background:#2c3e50">HABLAR</a>
                </div>""", unsafe_allow_html=True)

                with st.expander(f"⚙️ Borrar Fila {i+2}"):
                    if st.text_input(f"Psw Ch {i}", type="password", key=f"p_h_{i}") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar", key=f"b_h_{i}"):
                            requests.get(f"{SCRIPT_BORRAR}?gid={GID_CHOFERES}&fila={i+2}")
                            st.cache_data.clear()
                            st.rerun()
        except: st.warning("Actualizando camiones...")

st.markdown("<br><center><p style='color:gray; font-size:10px;'>v2.0 - San Jorge</p></center>", unsafe_allow_html=True)
