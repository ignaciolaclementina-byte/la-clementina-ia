import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN CENTRALIZADA ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    
ADMIN_PASSWORD = "1323" 

# TU URL DE GOOGLE APPS SCRIPT (Asegurate de que sea la última versión implementada)
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwtc_n-zJL-yS-3wpQAXW6mYOALNb19vsiOYCDBWbc-tWsiSCdSh1_AC-3Mon--vZ3E/exec"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- FUNCIONES DE DATOS ---
@st.cache_data(ttl=2)
def get_data(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&t={int(time.time())}"
    try:
        return pd.read_csv(url).fillna("-")
    except:
        return pd.DataFrame()

def ejecutar_accion(params):
    try:
        response = requests.get(SCRIPT_URL, params=params)
        return response.status_code == 200
    except:
        return False

# --- 2. DISEÑO Y ESTILOS CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 60px !important; background-color: #2c3e50 !important;
        border-radius: 10px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important; margin: 5px;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 12px; padding: 15px; margin-bottom: 12px;
        border-left: 10px solid #3498db; color: #333; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; margin-bottom: 5px; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 10px; 
        border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; height: 3em; }
    label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES Y REFRESH ---
col_b1, col_b2, col_ref = st.columns([2, 2, 1])
with col_b1: b_origen = st.text_input("🔍 ORIGEN:").strip()
with col_b2: b_destino = st.text_input("🏁 DESTINO:").strip()
with col_ref:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR"):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve Cargas / Publica Camión)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("<h3 style='color:white;'>📢 Publicar Camión</h3>", unsafe_allow_html=True)
        with st.form("form_chofer", clear_on_submit=True):
            ch_o = st.text_input("📍 Mi Ubicación")
            ch_d = st.text_input("🏁 Mi Destino")
            ch_e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            ch_w = st.text_input("📱 Mi WhatsApp (Ej: 3406441234)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                if ch_o and ch_d and ch_w:
                    p = {"action": "publicar", "tipo": "chofer", "orig": ch_o, "dest": ch_d, "equi": ch_e, "wsp": ch_w}
                    if ejecutar_accion(p):
                        st.success("✅ ¡Publicado!"); st.cache_data.clear(); time.sleep(1); st.rerun()
                    else: st.error("❌ Error al conectar con el servidor.")
                else: st.warning("⚠️ Completá todos los campos.")

    with col_d:
        st.markdown("<h3 style='color:white;'>📦 Cargas Disponibles</h3>", unsafe_allow_html=True)
        df_c = get_data(GID_CARGAS)
        if not df_c.empty:
            for i, r in df_c.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                # Mensaje Pro para WhatsApp
                msg = urllib.parse.quote(f"*RETORNO MATCH* 🚛\nHola! Te contacto por la carga:\n📍 *ORIGEN:* {r[1]}\n🏁 *DESTINO:* {r[2]}\n📦 *CARGA:* {r[3]}\n🏢 *EMPRESA:* {r[5]}\n\n¿Sigue disponible?")
                link = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}"
                
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <b>📦 CARGA:</b> {r[3]} | <b>🏢 EMPRESA:</b> {r[5]}<br>
                    <a href="{link}" target="_blank" class="btn-wsp">TOMAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"🗑️ Admin: Borrar Carga {i+2}"):
                    if st.text_input(f"Clave C-{i}", type="password") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar Borrar", key=f"del_c_{i}"):
                            if ejecutar_accion({"gid": GID_CARGAS, "fila": i+2}):
                                st.cache_data.clear(); st.rerun()

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve Camiones / Publica Carga)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("<h3 style='color:white;'>🏢 Publicar Carga</h3>", unsafe_allow_html=True)
        with st.form("form_empresa", clear_on_submit=True):
            em_o = st.text_input("📍 Retiro")
            em_d = st.text_input("🏁 Entrega")
            em_c = st.text_input("📦 Mercadería")
            em_n = st.text_input("🏢 Empresa")
            em_w = st.text_input("📱 WhatsApp de contacto")
            if st.form_submit_button("SUBIR CARGA"):
                if em_o and em_d and em_w:
                    p = {"action": "publicar", "tipo": "carga", "reti": em_o, "entreg": em_d, "merc": em_c, "empr": em_n, "wsp": em_w}
                    if ejecutar_accion(p):
                        st.success("✅ ¡Carga subida!"); st.cache_data.clear(); time.sleep(1); st.rerun()
                    else: st.error("❌ Error de servidor.")
                else: st.warning("⚠️ Completá todos los campos.")

    with col_b:
        st.markdown("<h3 style='color:white;'>🚛 Camiones Disponibles</h3>", unsafe_allow_html=True)
        df_h = get_data(GID_CHOFERES)
        if not df_h.empty:
            for i, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                msg_h = urllib.parse.quote(f"*RETORNO MATCH* 🚛\nHola! Vi tu camión disponible de *{r[1]}* a *{r[2]}*.\n⚙️ *EQUIPO:* {r[3]}\n\nTengo una carga que te puede interesar. ¿Estás disponible?")
                link_h = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={msg_h}"
                
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #2ecc71;">
                    <div class="route-txt">🚛 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <b>⚙️ EQUIPO:</b> {r[3]} | 📱 {r[4]}<br>
                    <a href="{link_h}" target="_blank" class="btn-wsp" style="background:#2c3e50">HABLAR CON CHOFER</a>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"🗑️ Admin: Borrar Camión {i+2}"):
                    if st.text_input(f"Clave Ch-{i}", type="password") == ADMIN_PASSWORD:
                        if st.button(f"Confirmar Borrar", key=f"del_h_{i}"):
                            if ejecutar_accion({"gid": GID_CHOFERES, "fila": i+2}):
                                st.cache_data.clear(); st.rerun()

st.markdown("<br><center><p style='color:white; opacity:0.5; font-size:12px;'>v3.5 Final - San Jorge, Sta Fe</p></center>", unsafe_allow_html=True)
