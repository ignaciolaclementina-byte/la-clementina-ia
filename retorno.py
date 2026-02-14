import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN (IDs Verificados con tus enlaces) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Hoja 6 (Camiones)
GID_CARGAS = "1267917528"    # Hoja 5 (Cargas)
ADMIN_PASSWORD = "1323" 

# URLs de envío (formResponse)
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. DISEÑO PREMIUM PARA CELULAR ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    
    /* PESTAÑAS GIGANTES */
    .stTabs [data-baseweb="tab-list"] { display: flex; gap: 8px; width: 100%; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 75px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important; border: 2px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border-color: white !important; }

    /* TARJETAS */
    .card-white {
        background: white !important; border-radius: 18px; padding: 18px; margin-bottom: 15px;
        border-left: 12px solid #3498db; box-shadow: 0 8px 15px rgba(0,0,0,0.3); color: #333;
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; margin-bottom: 8px; }
    .info-tag { 
        background: #f1f2f6; padding: 6px 12px; border-radius: 8px; font-size: 14px; 
        color: #444; border: 1px solid #ddd; margin: 3px; display: inline-block; font-weight: 600;
    }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 14px; 
        border-radius: 12px; text-decoration: none; font-weight: 900; display: block; text-align: center; margin-top: 12px;
        font-size: 16px; box-shadow: 0 4px 10px rgba(37, 211, 102, 0.4);
    }
    h1, h3, p, label { color: white !important; font-family: 'Arial', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; font-size: 42px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_origen = st.text_input("🔍 ORIGEN:").strip()
with c2: b_destino = st.text_input("🏁 DESTINO:").strip()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve Cargas / Publica Camión)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    
    with col_i:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_chofer", clear_on_submit=True):
            ch_o = st.text_input("📍 Mi Ubicación actual")
            ch_d = st.text_input("🏁 Mi Destino")
            ch_e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Térmico", "Batea"])
            ch_w = st.text_input("📱 Mi WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                data_ch = {
                    "entry.1304806144": ch_o, "entry.1519265625": ch_d,
                    "entry.597193898": ch_e, "entry.1574172378": ch_w
                }
                requests.post(URL_CHOFERES_POST, data=data_ch)
                st.success("✅ ¡Publicado! Revisá la pestaña 'SOY EMPRESA'"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            url_cargas = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
            df_c = pd.read_csv(url_cargas).fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                # Col B(1):Retiro, C(2):Entrega, D(3):Carga, E(4):WSP, F(5):Empresa, G(6):Fecha
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                # --- MENSAJE DE WHATSAPP PROFESIONAL ---
                txt = f"""*RETORNO MATCH* 🚛
Hola! Te contacto por la carga publicada:
📍 *ORIGEN:* {r[1]}
🏁 *DESTINO:* {r[2]}
📦 *CARGA:* {r[3]}
🏢 *EMPRESA:* {r[5]}

¿Sigue disponible? Soy chofer y estoy interesado."""
                
                txt_url = urllib.parse.quote(txt)
                link = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_url}"
                
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <div>
                        <span class="info-tag">🏢 {r[5]}</span>
                        <span class="info-tag">📦 {r[3]}</span>
                        <span class="info-tag">⏳ {r[6]}</span>
                    </div>
                    <a href="{link}" target="_blank" class="btn-wsp">TOMAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando con base de datos...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve Camiones / Publica Carga)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_empresa", clear_on_submit=True):
            em_o = st.text_input("📍 Ciudad Retiro")
            em_d = st.text_input("🏁 Ciudad Entrega")
            em_c = st.text_input("📦 Mercadería")
            em_n = st.text_input("🏢 Empresa")
            em_f = st.selectbox("⏳ Cuándo", ["Sale hoy", "Sale mañana", "A convenir"])
            em_w = st.text_input("📱 WhatsApp de contacto")
            if st.form_submit_button("SUBIR CARGA"):
                data_em = {
                    "entry.610070407": em_o, "entry.170847116": em_d, "entry.576675281": em_c,
                    "entry.1930562861": em_n, "entry.1064058502": em_f, "entry.466540450": em_w
                }
                requests.post(URL_CARGAS_POST, data=data_em)
                st.success("✅ ¡Carga subida!"); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
            df_h = pd.read_csv(url_ch).fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                # Col B(1):Origen, C(2):Destino, D(3):Equipo, E(4):WSP
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                # --- MENSAJE DE WHATSAPP PROFESIONAL ---
                txt_h = f"""*RETORNO MATCH* 🚛
Hola! Vi tu camión disponible:
📍 *TRAYECTO:* {r[1]} a {r[2]}
⚙️ *EQUIPO:* {r[3]}

Tengo una carga que te puede interesar. ¿Estás disponible?"""
                
                txt_h_url = urllib.parse.quote(txt_h)
                link_h = f"https://api.whatsapp.com/send?phone=549{r[4]}&text={txt_h_url}"
                
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #2ecc71;">
                    <div class="route-txt">🚛 {str(r[1]).upper()} ➔ {str(r[2]).upper()}</div>
                    <div>
                        <span class="info-tag">⚙️ {r[3]}</span>
                        <span class="info-tag">📱 {r[4]}</span>
                    </div>
                    <a href="{link_h}" target="_blank" class="btn-wsp" style="background:#2c3e50">HABLAR CON CHOFER</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones nuevos...")

# --- PANEL DE CONTROL ---
with st.expander("🔐 ADMINISTRADOR (Clave: 1323)"):
    if st.text_input("Contraseña", type="password") == ADMIN_PASSWORD:
        st.warning("⚠️ Para borrar una carga, eliminala directamente de tu Google Sheets.")
        st.write("**Vista rápida de filas:**")
        st.dataframe(pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").tail(5))

st.markdown("<br><center><p style='opacity:0.6; font-size:12px;'>© 2026 RETORNO MATCH - San Jorge, Santa Fe</p></center>", unsafe_allow_html=True)
