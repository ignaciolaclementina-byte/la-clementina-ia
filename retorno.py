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

# URLs de Google Forms y Apps Script
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
SCRIPT_BORRAR = "https://script.google.com/macros/s/AKfycbwtc_n-zJL-yS-3wpQAXW6mYOALNb19vsiOYCDBWbc-tWsiSCdSh1_AC-3Mon--vZ3E/exec"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. DISEÑO ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; margin: 5px;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 15px; margin-bottom: 12px;
        border-left: 10px solid #3498db; color: #333;
    }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 10px; 
        border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_origen = st.text_input("🔍 ORIGEN:").strip()
with c2: b_destino = st.text_input("🏁 DESTINO:").strip()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve Cargas)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2])
    with col_i:
        st.markdown("### 📢 Publicar Camión")
        with st.form("f_chofer", clear_on_submit=True):
            ch_o = st.text_input("📍 Ubicación actual")
            ch_d = st.text_input("🏁 Destino")
            ch_e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea"])
            ch_w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": ch_o, "entry.1519265625": ch_d, "entry.597193898": ch_e, "entry.1574172378": ch_w})
                st.success("✅ Publicado"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            for i, r in df_c.iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                txt = urllib.parse.quote(f"*RETORNO MATCH*\nHola! Me interesa la carga de {r[1]} a {r[2]}.")
                link = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={txt}"
                
                st.markdown(f"""<div class="card-white">
                    <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                    <b>📦 Carga:</b> {r[3]} | <b>🏢 Empresa:</b> {r[5]}<br>
                    <a href="{link}" target="_blank" class="btn-wsp">CONTACTAR EMPRESA</a>
                </div>""", unsafe_allow_html=True)
                
                # Botón de borrar para el Admin
                with st.expander(f"⚙️ Admin: Borrar Carga {i+2}"):
                    if st.text_input(f"Clave borrar carga {i}", type="password") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar Borrar Fila {i+2}", key=f"del_c_{i}"):
                            requests.get(f"{SCRIPT_BORRAR}?gid={GID_CARGAS}&fila={i+2}")
                            st.error("Eliminado"); time.sleep(1); st.rerun()
        except: st.write("Cargando datos...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve Camiones)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_empresa", clear_on_submit=True):
            em_o = st.text_input("📍 Retiro")
            em_d = st.text_input("🏁 Entrega")
            em_c = st.text_input("📦 Carga")
            em_n = st.text_input("🏢 Empresa")
            em_w = st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": em_o, "entry.170847116": em_d, "entry.576675281": em_c, "entry.1930562861": em_n, "entry.466540450": em_w})
                st.success("✅ Carga subida"); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            for i, r in df_h.iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                txt_h = urllib.parse.quote(f"*RETORNO MATCH*\nHola! Vi tu camión {r[3]} disponible de {r[1]} a {r[2]}.")
                link_h = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_h}"
                
                st.markdown(f"""<div class="card-white" style="border-left-color:#2ecc71">
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <b>⚙️ Equipo:</b> {r[3]}<br>
                    <a href="{link_h}" target="_blank" class="btn-wsp" style="background:#2c3e50">HABLAR CON CHOFER</a>
                </div>""", unsafe_allow_html=True)

                with st.expander(f"⚙️ Admin: Borrar Camión {i+2}"):
                    if st.text_input(f"Clave borrar chofer {i}", type="password") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar Borrar Fila {i+2}", key=f"del_h_{i}"):
                            requests.get(f"{SCRIPT_BORRAR}?gid={GID_CHOFERES}&fila={i+2}")
                            st.error("Eliminado"); time.sleep(1); st.rerun()
        except: st.write("Cargando datos...")

st.markdown("<br><center><p style='color:gray;'>© 2026 RETORNO MATCH - San Jorge</p></center>", unsafe_allow_html=True)
