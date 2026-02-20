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

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS POTENCIADOS ---
st.markdown("""
    <style>
    /* Fondo y Contenedor Principal */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1501700489910-fb245e85698b?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    
    /* Estilo de Pestañas */
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 60px !important; background-color: #1e272e !important;
        border-radius: 10px 10px 0 0 !important; color: #ecf0f1 !important; font-size: 16px !important;
        font-weight: 700 !important; margin: 2px; border: none !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; color: white !important; }

    /* Tarjetas (Cards) */
    .card-match {
        background: #ffffff !important;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        border-top: 5px solid #3498db;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        color: #2c3e50;
    }
    .route-title { 
        font-size: 20px; font-weight: 800; color: #2980b9; 
        display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 10px;
    }
    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; }
    .info-item { display: flex; align-items: center; gap: 5px; color: #555; }
    
    /* Botones */
    .btn-container { display: flex; gap: 8px; margin-top: 15px; }
    .btn-action {
        flex: 1; text-align: center; padding: 10px; border-radius: 8px;
        text-decoration: none; font-weight: 700; font-size: 14px; transition: 0.3s;
    }
    .btn-wsp { background-color: #25D366; color: white !important; }
    .btn-wsp:hover { background-color: #1eb954; transform: translateY(-2px); }
    .btn-doc { background-color: #3498db; color: white !important; }
    .btn-doc:hover { background-color: #2980b9; transform: translateY(-2px); }
    
    .badge-status { 
        font-size: 11px; font-weight: 900; padding: 3px 8px; border-radius: 5px; 
        float: right; text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white; font-weight:900;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
with st.container():
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: b_origen = st.text_input("🔍 Origen de viaje", placeholder="Ej: Rosario").strip()
    with c2: b_destino = st.text_input("🏁 Destino de viaje", placeholder="Ej: San Jorge").strip()
    with c3:
        st.write("<br>", unsafe_allow_html=True)
        if st.button("🔄 ACTUALIZAR", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 BUSCO CARGAS (Soy Chofer)", "🏢 BUSCO CAMIONES (Soy Empresa)"])

# ==========================================
# PESTAÑA CHOFER: Ver Cargas de Empresas
# ==========================================
with tab_chofer:
    col_f, col_l = st.columns([1, 2.2])
    with col_f:
        st.markdown("<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; color:white;'>", unsafe_allow_html=True)
        st.subheader("📢 Mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o, d = st.text_input("📍 Desde"), st.text_input("🏁 Hasta")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp")
            cuit, linti = st.text_input("🆔 CUIT"), st.text_input("💳 LINTI")
            doc = st.text_input("📂 Link Papeles")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                data = {"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1574172378": w, "entry.1542650763": cuit, "entry.1837643722": linti, "entry.769375120": doc}
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_l:
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                msg = urllib.parse.quote(f"Hola {r[5]}! Vi tu carga de {r[1]} a {r[2]} en Retorno Match.")
                st.markdown(f"""
                <div class="card-match">
                    <div class="route-title">📍 {r[1]} ➔ {r[2]}</div>
                    <div class="info-grid">
                        <div class="info-item">📦 <b>Carga:</b> {r[3]}</div>
                        <div class="info-item">🏢 <b>Empresa:</b> {r[5]}</div>
                        <div class="info-item">⏳ <b>Disponibilidad:</b> {r[6]}</div>
                    </div>
                    <div class="btn-container">
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg}" target="_blank" class="btn-action btn-wsp">💬 CONTACTAR EMPRESA</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Cargando oportunidades...")

# ==========================================
# PESTAÑA EMPRESA: Ver Camiones de Choferes
# ==========================================
with tab_empresa:
    col_fe, col_le = st.columns([1, 2.2])
    with col_fe:
        st.markdown("<div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; color:white;'>", unsafe_allow_html=True)
        st.subheader("🏢 Nueva Carga")
        with st.form("f_em", clear_on_submit=True):
            eo, ed, ec, en = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Mercadería"), st.text_input("Empresa")
            ef, ew = st.selectbox("⏳ Cuándo", ["Hoy", "Mañana", "A convenir"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA", use_container_width=True):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":eo,"entry.170847116":ed,"entry.576675281":ec,"entry.1930562861":en,"entry.1064058502":ef,"entry.466540450":ew})
                st.success("Carga subida!"); time.sleep(1); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with col_le:
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                is_verif = "VERIFICADO" in str(r[8]).upper()
                st.markdown(f"""
                <div class="card-match" style="border-top-color: {'#2ecc71' if is_verif else '#f1c40f'};">
                    <span class="badge-status" style="background:{'#2ecc71' if is_verif else '#f1c40f'}; color:white;">
                        {'Verificado' if is_verif else 'Pendiente'}
                    </span>
                    <div class="route-title">🚛 {r[1]} ➔ {r[2]}</div>
                    <div class="info-grid">
                        <div class="info-item">⚙️ <b>Equipo:</b> {r[3]}</div>
                        <div class="info-item">🆔 <b>CUIT:</b> {r[5]}</div>
                        <div class="info-item">💳 <b>LINTI:</b> {r[6]}</div>
                    </div>
                    <div class="btn-container">
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}" target="_blank" class="btn-action btn-wsp">💬 HABLAR CON CHOFER</a>
                        <a href="{r[7]}" target="_blank" class="btn-action btn-doc">📂 VER PAPELES</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando camiones...")

# --- FOOTER ---
st.markdown("<div style='text-align:center; padding:50px; color:white; opacity:0.6; font-size:12px;'>© 2026 RETORNO MATCH - San Jorge, Santa Fe | Desarrollado por Ignacio Díaz</div>", unsafe_allow_html=True)
