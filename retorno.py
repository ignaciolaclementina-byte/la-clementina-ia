import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- CONFIGURACIÓN DE IDs (Según tus capturas de Google Sheets) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

# URLs para el envío de datos (Google Forms)
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- ESTILOS VISUALES (Mantenimiento de tu interfaz) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .card-white {
        background: white !important; border-radius: 10px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #2ecc71; color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .card-carga { border-left-color: #3498db; }
    .route-txt { font-size: 22px; font-weight: 800; color: #1e3799; text-transform: uppercase; }
    .badge-verif { background: #2ecc71; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; float: right; }
    .badge-pend { background: #f1c40f; color: #333; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; float: right; }
    .btn-wsp { background: #25D366; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; width: 48%; margin-top: 10px; }
    .btn-doc { background: #3498db; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; text-align: center; width: 48%; margin-top: 10px; margin-left: 2%; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGACIÓN (Botones en lugar de pestañas) ---
if 'perfil' not in st.session_state:
    st.session_state.perfil = 'chofer'

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🚀 SOY CHOFER", use_container_width=True, type="primary" if st.session_state.perfil == 'chofer' else "secondary"):
        st.session_state.perfil = 'chofer'
with col_nav2:
    if st.button("🏢 SOY EMPRESA", use_container_width=True, type="primary" if st.session_state.perfil == 'empresa' else "secondary"):
        st.session_state.perfil = 'empresa'

# --- BUSCADORES ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with c_b2: b_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 REFRESCAR APP", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# MODO CHOFER: BUSCA CARGAS
# ==========================================
if st.session_state.perfil == 'chofer':
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.subheader("📢 Publicar mi Camión")
        with st.form("form_camion", clear_on_submit=True):
            u_o = st.text_input("📍 Ubicación Actual")
            u_d = st.text_input("🏁 Destino")
            u_e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            u_w = st.text_input("📱 WhatsApp (Sin 0 ni 15)")
            u_cuit = st.text_input("🆔 CUIT")
            u_linti = st.text_input("💳 LINTI")
            u_doc = st.text_input("📂 Link Documentación")
            
            if st.form_submit_button("PUBLICAR CAMIÓN"):
                payload = {
                    "entry.1304806144": u_o, "entry.1519265625": u_d, "entry.597193898": u_e,
                    "entry.1574172378": u_w, "entry.1542650763": u_cuit, "entry.1837643722": u_linti, "entry.769375120": u_doc
                }
                res = requests.post(URL_CHOFERES_POST, data=payload)
                if res.status_code == 200:
                    st.success("✅ Camión publicado!")
                    time.sleep(1); st.rerun()
                else: st.error("Fallo al subir datos.")

    with col_der:
        st.subheader("📦 Cargas Disponibles")
        try:
            url_c = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
            df_c = pd.read_csv(url_c).dropna(subset=["Punto de Retiro"])
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                    msg = urllib.parse.quote(f"Hola! Me interesa la carga {r[1]} -> {r[2]}")
                    st.markdown(f"""
                        <div class="card-white card-carga">
                            <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                            <b>Mercadería:</b> {r[3]} | <b>Empresa:</b> {r[5]}<br>
                            <b>Carga:</b> {r[6]}
                            <div style="margin-top:10px;">
                                <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" class="btn-wsp">💬 HABLAR CON EMPRESA</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("No hay cargas activas en este momento.")

# ==========================================
# MODO EMPRESA: BUSCA CAMIONES
# ==========================================
else:
    col_izq, col_der = st.columns([1, 2])
    
    with col_izq:
        st.subheader("🏢 Publicar Carga")
        with st.form("form_carga", clear_on_submit=True):
            e_o = st.text_input("📍 Origen")
            e_d = st.text_input("🏁 Destino")
            e_m = st.text_input("📦 Carga")
            e_n = st.text_input("Empresa")
            e_f = st.selectbox("⏳ Cuándo", ["Hoy", "Mañana", "Sin apuro"])
            e_w = st.text_input("📱 WhatsApp Empresa")
            
            if st.form_submit_button("SUBIR CARGA"):
                payload_e = {
                    "entry.610070407": e_o, "entry.170847116": e_d, "entry.576675281": e_m,
                    "entry.1930562861": e_n, "entry.1064058502": e_f, "entry.466540450": e_w
                }
                res_e = requests.post(URL_CARGAS_POST, data=payload_e)
                if res_e.status_code == 200:
                    st.success("✅ Carga publicada!")
                    time.sleep(1); st.rerun()
                else: st.error("Error al subir. Revisar IDs.")

    with col_der:
        st.subheader("🚛 Camiones Disponibles")
        try:
            url_h = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
            df_h = pd.read_csv(url_h).dropna(subset=["Origen"])
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                    status = '<span class="badge-verif">VERIFICADO</span>' if "VERIFICADO" in str(r[8]).upper() else '<span class="badge-pend">PENDIENTE</span>'
                    st.markdown(f"""
                        <div class="card-white">
                            {status}
                            <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                            <b>⚙️ EQUIPO:</b> {r[3]} | <b>🆔 CUIT:</b> {r[5]}<br>
                            <b>💳 LINTI:</b> {r[6]}
                            <div>
                                <a href="https://api.whatsapp.com/send?phone=549{r[4]}" class="btn-wsp">💬 HABLAR CON CHOFER</a>
                                <a href="{r[7]}" target="_blank" class="btn-doc">📂 PAPELES</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
        except: st.info("Sincronizando con Excel...")

st.markdown('<div style="text-align:center; color:white; padding:40px; opacity:0.5;">© 2026 RETORNO MATCH - San Jorge, Santa Fe</div>', unsafe_allow_html=True)
