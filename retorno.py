import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN (Verificada con tus links) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- ESTILOS CSS ---
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
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .badge-verif { color: #2ecc71; font-weight: 900; font-size: 14px; border: 2px solid #2ecc71; padding: 4px 10px; border-radius: 20px; float: right; }
    .footer { text-align: center; color: white; opacity: 0.8; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with c_b2: b_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 REFRESCAR DATOS", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- FUNCIÓN DE CARGA SEGURA ---
def leer_datos(gid):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&t={int(time.time())}"
        df = pd.read_csv(url)
        # Limpieza: quitar filas donde la segunda columna esté vacía (el Origen)
        df = df.dropna(subset=[df.columns[1]])
        return df
    except:
        return pd.DataFrame()

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve Cargas)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("### 📢 Publicar Camión")
        with st.form("form_ch", clear_on_submit=True):
            o, d = st.text_input("📍 Ubicación"), st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp")
            cuit, linti = st.text_input("🆔 CUIT"), st.text_input("💳 LINTI")
            link_doc = st.text_input("📂 Link Papeles")
            if st.form_submit_button("PUBLICAR"):
                payload = {
                    "entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e,
                    "entry.1542650763": cuit, "entry.1837643722": linti, 
                    "entry.769375120": link_doc, "entry.1574172378": w
                }
                requests.post(URL_CHOFERES_POST, data=payload)
                st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        df_c = leer_datos(GID_CARGAS)
        if df_c.empty:
            st.info("No se encontraron cargas. Revisá que el Excel sea público.")
        else:
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                msg = urllib.parse.quote(f"*RETORNO MATCH*\nMe interesa tu carga: {r[1]} -> {r[2]}")
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                    <b>📦 {r[3]}</b> | 🏢 {r[5]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve Camiones)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("form_em", clear_on_submit=True):
            eo, ed, ec, en = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Carga"), st.text_input("Empresa")
            ef = st.selectbox("⏳ Cuándo", ["Hoy", "Mañana", "Sin apuro"])
            ew = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("SUBIR CARGA"):
                payload = {
                    "entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec,
                    "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew
                }
                res = requests.post(URL_CARGAS_POST, data=payload)
                if res.status_code == 200:
                    st.success("✅ ¡Carga subida!"); time.sleep(2); st.rerun()
                else:
                    st.error(f"Error {res.status_code} al subir.")

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        df_h = leer_datos(GID_CHOFERES)
        if df_h.empty:
            st.info("No hay camiones registrados.")
        else:
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                # Manejo de verificación
                is_v = "VERIFICADO" in str(r[8]).upper() if len(r) > 8 else False
                badge = '<div class="badge-verif">✅ VERIFICADO</div>' if is_v else ''
                
                st.markdown(f"""
                <div class="card-white">
                    {badge}
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <b>⚙️ {r[3]}</b> | 🆔 CUIT: {r[4]}<br>
                    <a href="https://api.whatsapp.com/send?phone=549{r[7]}" target="_blank" class="btn-wsp">💬 HABLAR CON CHOFER</a>
                </div>
                """, unsafe_allow_html=True)

st.markdown(f'<div class="footer"><p>© 2026 <b>RETORNO MATCH</b> - San Jorge, Santa Fe</p></div>', unsafe_allow_html=True)
