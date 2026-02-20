import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN (VERSION FINAL BLINDADA) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    
ADMIN_PASSWORD = "1323" 

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS Y DISEÑO ---
st.markdown("""
    <style>
    .stApp {
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
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .footer { text-align: center; color: white; opacity: 0.9; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .legal { font-size: 10px; color: #bdc3c7; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- FUNCIONES ---
def enviar_a_google(url, data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        res = requests.post(url, data=data, headers=headers)
        return res.status_code == 200
    except: return False

# --- BÚSQUEDA ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 ORIGEN:")
with c_b2: b_destino = st.text_input("🏁 DESTINO:")
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- PESTAÑA 1: CHOFER (Busca Cargas) ---
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("<h3 style='color:white;'>📢 Publicar Camión</h3>", unsafe_allow_html=True)
        with st.form("form_ch", clear_on_submit=True):
            o = st.text_input("📍 Ubicación"); d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp"); cuit = st.text_input("🆔 CUIT")
            linti = st.text_input("💳 LINTI"); ld = st.text_input("📂 Link Documentación")
            if st.form_submit_button("PUBLICAR"):
                payload = {"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1542650763": cuit, "entry.1837643722": linti, "entry.769375120": ld, "entry.1574172378": w}
                if enviar_a_google(URL_CHOFERES_POST, payload):
                    st.success("✅ Publicado"); time.sleep(1); st.rerun()

    with col_d:
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                    # MENSAJE DE WHATSAPP MEJORADO
                    msg = urllib.parse.quote(f"Hola! Vi tu carga en *RETORNO MATCH*:\n📍 Origen: {r[1]}\n🏁 Destino: {r[2]}\n📦 Carga: {r[3]}\n¿Sigue disponible?")
                    st.markdown(f'<div class="card-white"><div class="route-txt">📍 {r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br><b>⏳ SALE:</b> {r[6]}<a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>', unsafe_allow_html=True)
        except: st.info("Actualizando...")

# --- PESTAÑA 2: EMPRESA (Busca Camiones) ---
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("<h3 style='color:white;'>🏢 Publicar Carga</h3>", unsafe_allow_html=True)
        with st.form("form_em", clear_on_submit=True):
            eo = st.text_input("📍 Origen"); ed = st.text_input("🏁 Destino"); ec = st.text_input("📦 Carga")
            en = st.text_input("Empresa"); ef = st.text_input("⏳ Cuándo"); ew = st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                payload = {"entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec, "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew}
                if enviar_a_google(URL_CARGAS_POST, payload):
                    st.success("✅ Carga subida"); time.sleep(1); st.rerun()

    with col_b:
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                    # MENSAJE DE WHATSAPP MEJORADO
                    msg_h = urllib.parse.quote(f"Hola! Vi tu camión en *RETORNO MATCH*:\n🚛 Equipo: {r[3]}\n📍 Ubicación: {r[1]}\n🏁 Destino: {r[2]}\n¿Estás disponible?")
                    st.markdown(f'<div class="card-white"><div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div><b>⚙️ EQUIPO:</b> {r[3]}<br><b>🆔 CUIT:</b> {r[5]}<div style="display:flex;gap:10px;"><a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg_h}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONTACTAR CHOFER</a><a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 DOCUMENTACIÓN</a></div></div>', unsafe_allow_html=True)
        except: st.info("Actualizando...")

# --- FOOTER CON LEGALES ---
st.markdown(f"""
    <div class="footer">
        <p><b>© 2026 RETORNO MATCH - San Jorge, Santa Fe</b></p>
        <p>Desarrollado por <b>Ignacio Diaz</b></p>
        <div class="legal">
            Queda prohibida la reproducción total o parcial de esta interfaz. 
            El uso de los datos publicados es responsabilidad exclusiva de las partes. 
            RETORNO MATCH no se responsabiliza por la veracidad de la documentación cargada.
        </div>
    </div>
    """, unsafe_allow_html=True)
