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

# URLs de Google Forms (Basado en tus estructuras)
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH | Panel", page_icon="🚛", layout="wide")

# --- 2. ESTILOS (ARREGLO PARA CELULAR) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    
    /* PESTAÑAS TIPO BOTÓN GIGANTE */
    .stTabs [data-baseweb="tab-list"] { display: flex; width: 100%; gap: 10px; padding: 10px 0; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 80px !important; background-color: #2c3e50 !important;
        border-radius: 15px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important; text-align: center; border: 2px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db !important; border: 2px solid white !important;
    }

    /* TARJETAS */
    .card-white {
        background: white !important; border-radius: 20px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 12px solid #3498db; box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    
    @media (max-width: 800px) {
        .card-white { flex-direction: column; align-items: stretch; text-align: left; }
        .btn-tomar { width: 100%; text-align: center; margin-top: 15px; padding: 18px; }
        .stTabs [data-baseweb="tab"] { font-size: 13px !important; height: 70px !important; }
    }

    .route-style { font-size: 22px; font-weight: 900; color: #1e3799 !important; margin-bottom: 10px; }
    .label-style { 
        background: #f8f9fa; padding: 8px 12px; border-radius: 10px; font-size: 14px; 
        color: #333; border: 1px solid #ddd; display: flex; align-items: center; gap: 5px; margin-bottom: 5px;
    }
    .label-style b { color: #1e3799; }
    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 12px 25px; 
        border-radius: 15px; text-decoration: none; font-weight: 900; font-size: 16px;
    }
    
    h1, h3, p, label { color: white !important; font-family: 'Arial', sans-serif; }
    .admin-panel { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 20px; border: 1px dashed white; margin-top: 40px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_orig = st.text_input("🔍 Buscar Origen:")
with c2: b_dest = st.text_input("🏁 Buscar Destino:")

t1, t2 = st.tabs(["🚀 SOY CHOFER (Ver Cargas)", "🏢 SOY EMPRESA (Ver Camiones)"])

# === PESTAÑA 1: CHOFERES ===
with t1:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o = st.text_input("📍 Mi Ubicación")
            d = st.text_input("🏁 Destino deseado")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado"])
            w = st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()
    
    with col_b:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            for _, r in df.iloc[::-1].iterrows():
                ret, ent, mer, tel, emp, urg = r[1], r[2], r[3], r[4], r[5], r[6]
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                # WHATSAPP CON TEXTO AUTOMÁTICO COMPLETO
                msg = f"¡Hola! Vi tu carga en Retorno Match 🚛\n\n📍 Origen: {ret}\n🏁 Destino: {ent}\n📦 Carga: {mer}\n🏢 Empresa: {emp}\n\n¿Sigue disponible? Soy chofer y me interesa."
                link = f"https://api.whatsapp.com/send?phone=549{tel}&text={urllib.parse.quote(msg)}"
                
                st.markdown(f"""
                    <div class="card-white">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <div class="label-style">🏢 <b>Empresa:</b> {emp}</div>
                                <div class="label-style">📦 <b>Carga:</b> {mer}</div>
                                <div class="label-style">⏳ <b>Urgencia:</b> {urg}</div>
                            </div>
                        </div>
                        <a href="{link}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Conectando con Excel...")

# === PESTAÑA 2: EMPRESAS ===
with t2:
    st.markdown("### 🚛 Camiones buscando carga")
    # (Aquí iría la lógica similar para ver choferes, respetando tu estructura actual)

# === 🔐 PANEL DE CONTROL (Borrar Cargas) ===
st.markdown("<div class='admin-panel'>", unsafe_allow_html=True)
st.markdown("### 🔐 Panel de Control (Solo Ignacio)")
pwd = st.text_input("Ingresar contraseña:", type="password")

if pwd == ADMIN_PASSWORD:
    st.info("Para borrar una carga, buscala en la lista y borrá la fila correspondiente en tu Google Sheets.")
    try:
        df_adm = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
        for i, row in df_adm.iterrows():
            st.write(f"Fila {i+2} ➔ {row[1]} a {row[2]} ({row[5]})")
    except: st.write("No hay datos.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><p style='text-align:center; opacity:0.5; font-size:12px;'>© 2026 RETORNO MATCH - San Jorge, Santa Fe</p>", unsafe_allow_html=True)
