import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN (IDs Verificados según tus capturas) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- ESTILOS MEJORADOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .card-white {
        background: white !important; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        border-left: 8px solid #3498db; color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .route-txt { font-size: 20px; font-weight: 800; color: #1e3799; text-transform: uppercase; margin-bottom: 5px;}
    .badge-verif { background: #2ecc71; color: white; padding: 3px 10px; border-radius: 15px; font-size: 11px; font-weight: bold; float: right; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-doc { background: #3498db; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 ORIGEN:").strip()
with c_b2: b_destino = st.text_input("🏁 DESTINO:").strip()
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 BUSCAR CARGA", "🏢 BUSCAR CAMIÓN"])

# ==========================================
# PESTAÑA 1: SOY CHOFER (Ve las Cargas de Empresas)
# ==========================================
with tab_chofer:
    col_i, col_d = st.columns([1, 2])
    with col_i:
        st.subheader("📢 Publicar mi Camión")
        with st.form("form_ch", clear_on_submit=True):
            o = st.text_input("📍 Ubicación Actual")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp (Sin 0 ni 15)")
            cuit = st.text_input("🆔 CUIT")
            linti = st.text_input("💳 LINTI")
            link_doc = st.text_input("📂 Link Documentación")
            if st.form_submit_button("PUBLICAR CAMIÓN"):
                data_ch = {
                    "entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e,
                    "entry.1574172378": w, "entry.1542650763": cuit, "entry.1837643722": linti, "entry.769375120": link_doc
                }
                res = requests.post(URL_CHOFERES_POST, data=data_ch)
                if res.status_code == 200: st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
                else: st.error(f"Error {res.status_code}. Revisar IDs del formulario.")

    with col_d:
        st.subheader("📦 Cargas para llevar")
        try:
            url_c = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
            df_c = pd.read_csv(url_c).dropna(subset=["Punto de Retiro"])
            if df_c.empty: st.info("No hay cargas activas.")
            else:
                for _, r in df_c.iloc[::-1].iterrows():
                    if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                        msg = urllib.parse.quote(f"Hola! Me interesa la carga {r[1]} -> {r[2]}")
                        st.markdown(f"""<div class="card-white">
                            <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                            <b>Mercadería:</b> {r[3]} | <b>Empresa:</b> {r[5]}<br>
                            <b>Carga:</b> {r[6]}
                            <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" class="btn-wsp">💬 CONTACTAR EMPRESA</a>
                        </div>""", unsafe_allow_html=True)
        except: st.warning("Esperando datos...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA (Ve los Camiones de Choferes)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("🏢 Publicar Carga")
        with st.form("form_em", clear_on_submit=True):
            eo, ed, ec, en = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Mercadería"), st.text_input("Empresa")
            ef = st.selectbox("⏳ Cuándo carga?", ["Hoy", "Mañana", "Sin apuro"])
            ew = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("SUBIR CARGA"):
                payload_em = {
                    "entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec,
                    "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew
                }
                res_em = requests.post(URL_CARGAS_POST, data=payload_em)
                if res_em.status_code == 200: st.success("✅ Carga subida!"); time.sleep(1); st.rerun()
                else: st.error(f"Error {res_em.status_code}. Google rechazó los datos.")

    with col_b:
        st.subheader("🚛 Camiones en zona")
        try:
            url_h = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
            df_h = pd.read_csv(url_h).dropna(subset=["Origen"])
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen.lower() in str(r[1]).lower() and b_destino.lower() in str(r[2]).lower():
                    status = '<span class="badge-verif">VERIFICADO</span>' if "VERIFICADO" in str(r[8]).upper() else ""
                    st.markdown(f"""<div class="card-white">
                        {status}
                        <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                        <b>Equipo:</b> {r[3]} | <b>CUIT:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}" class="btn-wsp">💬 HABLAR CON CHOFER</a>
                        <a href="{r[7]}" target="_blank" class="btn-doc">📂 VER DOCUMENTACIÓN</a>
                    </div>""", unsafe_allow_html=True)
        except: st.info("Sincronizando...")

st.markdown('<div style="text-align:center; color:white; padding:20px; opacity:0.6;">© 2026 RETORNO MATCH</div>', unsafe_allow_html=True)
