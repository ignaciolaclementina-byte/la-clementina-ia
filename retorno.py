import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Hoja CHOFERES
GID_CARGAS = "1267917528"    # Hoja CARGAS
ADMIN_PASSWORD = "1323" 

# URLs de Google Forms (Basado en tus capturas)
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS PERSONALIZADOS ---
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
        font-weight: 900 !important; margin: 5px; border: 1px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    label { color: white !important; font-weight: bold; font-size: 16px; }
    .footer { text-align: center; color: white; opacity: 0.8; padding: 30px; font-size: 14px; border-top: 1px solid #444; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white; font-size: 45px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES Y BOTÓN ACTUALIZAR ---
col_bus1, col_bus2, col_act = st.columns([2, 2, 1])
with col_bus1: b_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with col_bus2: b_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with col_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("### 📢 Publicar Camión")
        with st.form("form_chofer", clear_on_submit=True):
            o = st.text_input("📍 Mi Ubicación")
            d = st.text_input("🏁 Mi Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp (Ej: 3406441234)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                if o and d and w:
                    payload = {"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1574172378": w}
                    requests.post(URL_CHOFERES_POST, data=payload)
                    st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                msg = urllib.parse.quote(f"Hola! Me interesa la carga {r[1]} -> {r[2]} vista en Retorno Match")
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <b>📦 CARGA:</b> {r[3]} | <b>🏢 EMPRESA:</b> {r[5]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" target="_blank" class="btn-wsp">TOMAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Cargando datos...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("form_empresa", clear_on_submit=True):
            em_o = st.text_input("📍 Punto de Retiro")
            em_d = st.text_input("🏁 Punto de Entrega")
            em_c = st.text_input("📦 ¿Qué cargás?")
            em_n = st.text_input("🏢 Empresa")
            em_f = st.selectbox("⏳ Cuándo", ["Sale hoy", "Sale mañana", "A convenir"])
            em_w = st.text_input("📱 WhatsApp de contacto")
            if st.form_submit_button("SUBIR CARGA"):
                if em_o and em_d and em_w:
                    payload_em = {"entry.610070407": em_o, "entry.170847116": em_d, "entry.576675281": em_c, "entry.1930562861": em_n, "entry.1064058502": em_f, "entry.466540450": em_w}
                    requests.post(URL_CARGAS_POST, data=payload_em)
                    st.success("✅ Carga subida exitosamente"); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #2ecc71;">
                    <div class="route-txt">🚛 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <b>⚙️ EQUIPO:</b> {r[3]} | 📱 {r[4]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}" target="_blank" class="btn-wsp" style="background:#2c3e50">HABLAR CON CHOFER</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones...")

# --- PANEL DE CONTROL ---
with st.expander("🔐 ADMINISTRADOR (Clave: 1323)"):
    if st.text_input("Psw", type="password") == ADMIN_PASSWORD:
        st.info("Para borrar datos, gestionarlos desde el Excel directamente.")

# --- PIE DE PÁGINA (DERECHOS DE AUTOR) ---
st.markdown(f"""
    <div class="footer">
        <p>© 2026 <b>RETORNO MATCH</b> - Todos los derechos reservados.</p>
        <p>Desarrollado por <b>Ignacio Díaz</b> | San Jorge, Santa Fe</p>
    </div>
    """, unsafe_allow_html=True)
