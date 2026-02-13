import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. ESTILOS DE ALTO IMPACTO (Especial para Celular) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    
    /* PESTAÑAS TIPO BOTÓN GIGANTE */
    .stTabs [data-baseweb="tab-list"] {
        display: flex; flex-direction: row; width: 100%; gap: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 10px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; text-align: center; border: 2px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important; border: 2px solid white !important;
        box-shadow: 0 0 15px rgba(52, 152, 219, 0.5);
    }

    /* TARJETAS MEJORADAS */
    .card-white {
        background: white !important; border-radius: 20px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 12px solid #3498db; box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    
    @media (max-width: 800px) {
        .card-white { flex-direction: column; align-items: stretch; text-align: left; }
        .btn-tomar { width: 100%; text-align: center; margin-top: 15px; height: 55px; display: flex; align-items: center; justify-content: center; }
        .stTabs [data-baseweb="tab"] { font-size: 14px !important; height: 60px !important; }
    }

    .route-style { font-size: 22px; font-weight: 900; color: #1e3799 !important; margin-bottom: 12px; }
    
    .label-style { 
        background: #f8f9fa; padding: 8px 15px; border-radius: 10px; font-size: 15px; 
        color: #2d3436; border: 1px solid #dfe6e9; display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
    }
    .label-style b { color: #1e3799; }

    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 15px 30px; 
        border-radius: 15px; text-decoration: none; font-weight: 900; font-size: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    h1, h3, p, label { color: white !important; font-family: 'Arial Black', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h1 style='font-size: 45px;'>🚛 RETORNO MATCH</h1></div>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2 = st.columns(2)
with c_b1: b_orig = st.text_input("🔍 ORIGEN:")
with c_b2: b_dest = st.text_input("🏁 DESTINO:")

# PESTAÑAS CLARAS
t1, t2 = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# === PESTAÑA 1: CHOFERES ===
with t1:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o, d, e, w = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Térmico"]), st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("¡Listo! Publicado."); st.rerun()
    
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("No especificado")
            for _, r in df.iloc[::-1].iterrows():
                ret, ent, mer, tel, emp, urg = r[1], r[2], r[3], r[4], r[5], r[6]
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                # MENSAJE DE WHATSAPP MEJORADO
                msg_final = f"¡Hola! Te contacto por Retorno Match 🚛\n\nVi tu carga disponible:\n📍 Origen: {ret}\n🏁 Destino: {ent}\n📦 Carga: {mer}\n🏢 Empresa: {emp}\n\n¿Sigue disponible? Soy chofer y me interesa."
                link_ws = f"https://api.whatsapp.com/send?phone=549{tel}&text={urllib.parse.quote(msg_final)}"
                
                st.markdown(f"""
                    <div class="card-white">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <div class="label-style">🏢 <b>Empresa:</b> {emp}</div>
                                <div class="label-style">📦 <b>Carga:</b> {mer}</div>
                                <div class="label-style">⏳ <b>Urgencia:</b> {urg}</div>
                                <div class="label-style">📱 <b>WhatsApp:</b> {tel}</div>
                            </div>
                        </div>
                        <a href="{link_ws}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Error de conexión.")

# === PESTAÑA 2: EMPRESAS ===
with t2:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga Nueva")
        with st.form("f2", clear_on_submit=True):
            eo, ed, em, en = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega"), st.text_input("📦 Carga (ej: 11 pallets)"), st.text_input("🏢 Empresa")
            eu, ew = st.selectbox("⏳ ¿Cuándo?", ["Hoy", "Mañana", "Sin apuro"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[5]:en, ID_EM[3]:ew, ID_EM[4]:eu})
                st.success("¡Carga en línea!"); st.rerun()
    
    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in dfh.iloc[::-1].iterrows():
                o_h, d_h, eq_h, tel_h = r[1], r[2], r[3], r[4]
                msg_ch = f"¡Hola! Te contacto por Retorno Match 🚛\n\nVi tu camión disponible de {o_h} hacia {d_h}.\n🚛 Equipo: {eq_h}.\n\n¿Seguís disponible? Tengo una carga."
                link_ch = f"https://api.whatsapp.com/send?phone=549{tel_h}&text={urllib.parse.quote(msg_ch)}"

                st.markdown(f"""
                    <div class="card-white" style="border-left-color: #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(o_h).upper()} ➔ {str(d_h).upper()}</p>
                            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                                <div class="label-style">⚙️ <b>Equipo:</b> {eq_h}</div>
                                <div class="label-style">📱 <b>Tel:</b> {tel_h}</div>
                            </div>
                        </div>
                        <a href="{link_ch}" target="_blank" class="btn-tomar" style="background:#2ecc71">HABLAR CON CHOFER</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

st.markdown("<br><hr><p style='text-align:center; opacity:0.6; font-size:12px; color:white;'>© 2026 RETORNO MATCH - Ignacio Diaz | San Jorge</p>", unsafe_allow_html=True)
