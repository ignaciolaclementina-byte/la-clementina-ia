import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# URLs de Google Forms (Mantengo tus IDs actuales)
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. LÓGICA DE APOYO ---
def obtener_color_urgencia(estado):
    est = str(estado).lower()
    if "hoy" in est: return "#FF4B4B"
    if "mañana" in est: return "#F1C40F"
    return "#3498DB"

# --- 3. ESTILOS (MEJORADOS PARA MÓVIL Y CLARIDAD) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    
    /* Tarjeta Blanca */
    .card-white {
        background: white !important; border-radius: 12px; padding: 15px; margin-bottom: 12px;
        display: flex; flex-direction: row; justify-content: space-between; align-items: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3); border-left: 10px solid #3498db;
    }
    
    /* Ajuste para celular */
    @media (max-width: 640px) {
        .card-white { flex-direction: column; align-items: flex-start; gap: 15px; }
        .btn-tomar { width: 100%; text-align: center; }
    }

    .route-style { font-size: 18px; font-weight: 800; color: #1e3799 !important; margin-bottom: 8px; text-transform: uppercase; }
    
    /* Cápsulas de información explicativas */
    .info-container { display: flex; flex-wrap: wrap; gap: 8px; }
    .label-style { 
        background: #f1f2f6; padding: 6px 12px; border-radius: 8px; font-size: 13px; 
        color: #2f3542; border: 1px solid #dcdde1; display: flex; align-items: center; gap: 5px; 
    }
    .label-style b { color: #1e3799; }

    /* Botón */
    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 12px 20px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 14px;
        white-space: nowrap; transition: 0.3s;
    }
    .btn-tomar:hover { background-color: #2980b9; }
    
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h1 style='font-size: 40px; font-weight: 900;'>🚛 RETORNO MATCH</h1></div>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2 = st.columns(2)
with c_b1: b_orig = st.text_input("🔍 Origen:")
with c_b2: b_dest = st.text_input("🏁 Destino:")

t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# === PESTAÑA 1: CHOFERES ===
with t1:
    col1, col2 = st.columns([1, 2.2])
    with col1:
        st.markdown("### 📢 Publicar Camión")
        with st.form("f1", clear_on_submit=True):
            o = st.text_input("📍 Origen")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider"])
            w = st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
    
    with col2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            for _, r in df.iloc[::-1].iterrows():
                # MAPEO SEGÚN TU EXCEL: B=1(Ret), C=2(Ent), D=3(Merc), E=4(WhatsApp), F=5(Emp), G=6(Urg)
                ret, ent, mer, tel, emp, urg = r[1], r[2], r[3], r[4], r[5], r[6]
                
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                color_urg = obtener_color_urgencia(urg)
                
                # LINK WHATSAPP CON TEXTO AUTOMÁTICO
                texto_ws = f"Hola! Vi tu carga de {ret} a {ent} ({mer}) en Retorno Match. ¿Sigue disponible?"
                link_ws = f"https://api.whatsapp.com/send?phone=549{tel}&text={urllib.parse.quote(texto_ws)}"
                
                st.markdown(f"""
                    <div class="card-white" style="border-left-color: {color_urg};">
                        <div>
                            <p class="route-style">📍 {ret} ➔ {ent}</p>
                            <div class="info-container">
                                <div class="label-style">🏢 <b>Empresa:</b> {emp}</div>
                                <div class="label-style">📦 <b>Carga:</b> {mer}</div>
                                <div class="label-style">⏳ <b>Sale:</b> {urg}</div>
                                <div class="label-style">📱 <b>Tel:</b> {tel}</div>
                            </div>
                        </div>
                        <a href="{link_ws}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Error cargando datos.")

# === PESTAÑA 2: EMPRESAS ===
with t2:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f2", clear_on_submit=True):
            eo = st.text_input("📍 Retiro")
            ed = st.text_input("🏁 Entrega")
            em = st.text_input("📦 Carga (ej: 11 pallets)")
            en = st.text_input("🏢 Empresa")
            eu = st.selectbox("⏳ ¿Cuándo?", ["Hoy", "Mañana", "Sin apuro"])
            ew = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[5]:en, ID_EM[3]:ew, ID_EM[4]:eu})
                st.success("✅ Carga subida!"); time.sleep(1); st.rerun()
    
    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in dfh.iloc[::-1].iterrows():
                o_h, d_h, eq_h, tel_h = r[1], r[2], r[3], r[4]
                link_h = f"https://api.whatsapp.com/send?phone=549{tel_h}&text=Hola! Vi tu camion disponible de {o_h} a {d_h} en Retorno Match."
                
                st.markdown(f"""
                    <div class="card-white" style="border-left-color: #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {o_h} ➔ {d_h}</p>
                            <div class="info-container">
                                <div class="label-style">⚙️ <b>Equipo:</b> {eq_h}</div>
                                <div class="label-style">📱 <b>WhatsApp:</b> {tel_h}</div>
                            </div>
                        </div>
                        <a href="{link_h}" target="_blank" class="btn-tomar" style="background:#2ecc71">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Error.")

st.markdown("<br><p style='text-align:center; opacity:0.5; font-size:12px;'>© 2026 RETORNO MATCH - Ignacio Diaz</p>", unsafe_allow_html=True)
