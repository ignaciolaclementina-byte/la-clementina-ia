import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN DE IDs ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

# URLs para el envío de datos
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS (Tu Interfaz Oscura) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .card-white {
        background: white !important; border-radius: 10px; padding: 20px; margin-bottom: 15px;
        color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .route-header { font-size: 24px; font-weight: 800; color: #1e3799; margin-bottom: 10px; }
    .badge-verif { background: #2ecc71; color: white; padding: 4px 12px; border-radius: 20px; float: right; font-size: 12px; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LÓGICA DE NAVEGACIÓN (Botones Superiores) ---
if 'perfil' not in st.session_state:
    st.session_state.perfil = 'chofer'

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# Botones de Perfil
c1, c2 = st.columns(2)
with c1:
    if st.button("🚀 SOY CHOFER", use_container_width=True, type="primary" if st.session_state.perfil == 'chofer' else "secondary"):
        st.session_state.perfil = 'chofer'
with c2:
    if st.button("🏢 SOY EMPRESA", use_container_width=True, type="primary" if st.session_state.perfil == 'empresa' else "secondary"):
        st.session_state.perfil = 'empresa'

# Buscadores
fb1, fb2, fba = st.columns([2, 2, 1])
with fb1: f_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with fb2: f_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with fba:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- 4. CONTENIDO PRINCIPAL (Dos Columnas) ---
col_form, col_list = st.columns([1, 2])

# MODO CHOFER: Publica Camión / Ve Cargas
if st.session_state.perfil == 'chofer':
    with col_form:
        st.subheader("📢 Publicar mi Camión")
        with st.form("f_chofer", clear_on_submit=True):
            o = st.text_input("Ubicación Actual")
            d = st.text_input("Destino")
            e = st.selectbox("Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("WhatsApp (Ej: 3406441234)")
            c = st.text_input("CUIT")
            l = st.text_input("LINTI")
            doc = st.text_input("Link Documentación")
            if st.form_submit_button("SUBIR CAMIÓN"):
                payload = {
                    "entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e,
                    "entry.1574172378": w, "entry.1542650763": c, "entry.1837643722": l, "entry.769375120": doc
                }
                res = requests.post(URL_CHOFERES_POST, data=payload)
                if res.status_code == 200: st.success("¡Publicado!"); time.sleep(1); st.rerun()
                else: st.error(f"Error {res.status_code}. Revisar IDs.")

    with col_list:
        st.subheader("📦 Cargas Disponibles")
        try:
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}"
            df = pd.read_csv(url).dropna(subset=["Punto de Retiro"])
            if df.empty: st.info("No hay cargas publicadas en el Excel.")
            else:
                for _, r in df.iloc[::-1].iterrows():
                    if f_origen.lower() in str(r[1]).lower() and f_destino.lower() in str(r[2]).lower():
                        st.markdown(f"""<div class="card-white">
                            <div class="route-header">📍 {r[1]} ➔ {r[2]}</div>
                            <b>Carga:</b> {r[3]} | <b>Empresa:</b> {r[5]}<br>
                            <a href="https://wa.me/549{r[4]}" class="btn-wsp">💬 CONTACTAR</a>
                        </div>""", unsafe_allow_html=True)
        except: st.warning("Sincronizando...")

# MODO EMPRESA: Publica Carga / Ve Camiones
else:
    with col_form:
        st.subheader("🏢 Publicar Carga")
        with st.form("f_empresa", clear_on_submit=True):
            eo = st.text_input("Origen")
            ed = st.text_input("Destino")
            ec = st.text_input("Carga")
            en = st.text_input("Empresa")
            ew = st.text_input("WhatsApp Empresa")
            if st.form_submit_button("SUBIR CARGA"):
                payload_e = {
                    "entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec,
                    "entry.1930562861": en, "entry.466540450": ew
                }
                res_e = requests.post(URL_CARGAS_POST, data=payload_e)
                if res_e.status_code == 200: st.success("Carga subida!"); time.sleep(1); st.rerun()
                else: st.error("Error 400 al subir. Revisar IDs.")

    with col_list:
        st.subheader("🚛 Camiones Disponibles")
        try:
            url_h = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}"
            df_h = pd.read_csv(url_h).dropna(subset=["Origen"])
            for _, r in df_h.iloc[::-1].iterrows():
                if f_origen.lower() in str(r[1]).lower() and f_destino.lower() in str(r[2]).lower():
                    st.markdown(f"""<div class="card-white">
                        <div class="route-header">🚛 {r[1]} ➔ {r[2]}</div>
                        <b>Equipo:</b> {r[3]} | <b>CUIT:</b> {r[5]}<br>
                        <a href="https://wa.me/549{r[4]}" class="btn-wsp">💬 HABLAR CON CHOFER</a>
                    </div>""", unsafe_allow_html=True)
        except: st.info("Buscando camiones...")

st.markdown('<p style="text-align:center; color:white; opacity:0.5; margin-top:50px;">© 2026 RETORNO MATCH - San Jorge</p>', unsafe_allow_html=True)
