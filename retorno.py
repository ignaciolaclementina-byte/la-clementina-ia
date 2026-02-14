import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (IDs Verificados) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Hoja 6: Donde publican los choferes
GID_CARGAS = "1267917528"    # Hoja 5: Donde publican las empresas
ADMIN_PASSWORD = "1323" 

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS (Optimizados para Celular) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab-list"] { display: flex; width: 100%; gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 75px !important; background-color: #2c3e50 !important;
        border-radius: 15px !important; color: white !important; font-size: 16px !important;
        font-weight: 900 !important; border: 2px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border: 2px solid white !important; }

    .card-white {
        background: white !important; border-radius: 20px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 12px solid #3498db; box-shadow: 0 10px 20px rgba(0,0,0,0.4); color: #333;
    }
    
    @media (max-width: 800px) {
        .card-white { flex-direction: column; align-items: stretch; }
        .btn-tomar { width: 100%; text-align: center; margin-top: 15px; padding: 18px; }
    }

    .route-style { font-size: 22px; font-weight: 900; color: #1e3799 !important; margin-bottom: 12px; }
    .label-style { 
        background: #f1f2f6; padding: 8px 12px; border-radius: 10px; font-size: 14px; 
        color: #333; border: 1px solid #ddd; display: flex; align-items: center; gap: 5px; margin-bottom: 5px;
    }
    .label-style b { color: #1e3799; }
    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 15px 25px; 
        border-radius: 15px; text-decoration: none; font-weight: 900; font-size: 16px; display: inline-block;
    }
    
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES (Si se escriben, filtran. Si están vacíos, muestran todo) ---
c1, c2 = st.columns(2)
with c1: b_orig = st.text_input("📍 ORIGEN (Ciudad):").strip()
with c2: b_dest = st.text_input("🏁 DESTINO (Ciudad):").strip()

tab1, tab2 = st.tabs(["🚀 SOY CHOFER (Ver Cargas)", "🏢 SOY EMPRESA (Ver Camiones)"])

# === PESTAÑA 1: SOY CHOFER (Muestra lo que cargan las empresas) ===
with tab1:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_chofer", clear_on_submit=True):
            orig = st.text_input("📍 Ubicación actual")
            dest = st.text_input("🏁 Destino buscado")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Térmico", "Acoplado"])
            wsp = st.text_input("📱 Tu WhatsApp (con código de área)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:orig, ID_CH[1]:dest, ID_CH[2]:equi, ID_CH[3]:wsp})
                st.success("✅ ¡Publicado! Revisá la pestaña 'SOY EMPRESA'"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas de Empresas")
        try:
            # Forzamos la descarga fresca del CSV
            url_cargas = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&cache={time.time()}"
            df_c = pd.read_csv(url_cargas).fillna("S/D")
            
            for _, r in df_c.iloc[::-1].iterrows():
                # B=1:Ret, C=2:Ent, D=3:Carga, E=4:WSP, F=5:Emp, G=6:Urg
                c_ret, c_ent, c_mer, c_tel, c_emp, c_urg = r[1], r[2], r[3], r[4], r[5], r[6]
                
                if b_orig and b_orig.lower() not in str(c_ret).lower(): continue
                if b_dest and b_dest.lower() not in str(c_ent).lower(): continue

                txt_w = f"¡Hola! Vi tu carga de {c_ret} a {c_ent} en Retorno Match 🚛\nCarga: {c_mer}\n¿Sigue disponible?"
                link_w = f"https://api.whatsapp.com/send?phone=549{c_tel}&text={urllib.parse.quote(txt_w)}"
                
                st.markdown(f"""
                    <div class="card-white">
                        <div>
                            <p class="route-style">📍 {str(c_ret).upper()} ➔ {str(c_ent).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <div class="label-style">🏢 <b>Empresa:</b> {c_emp}</div>
                                <div class="label-style">📦 <b>Carga:</b> {c_mer}</div>
                                <div class="label-style">⏳ <b>Sale:</b> {c_urg}</div>
                            </div>
                        </div>
                        <a href="{link_w}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Sincronizando con la base de datos...")

# === PESTAÑA 2: SOY EMPRESA (Muestra los camiones de los choferes) ===
with tab2:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("f_empresa", clear_on_submit=True):
            e_o, e_d, e_m, e_e = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Carga"), st.text_input("🏢 Empresa")
            e_u = st.selectbox("⏳ ¿Cuándo?", ["Hoy", "Mañana", "Sin apuro"])
            e_w = st.text_input("📱 WhatsApp contacto")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:e_o, ID_EM[1]:e_d, ID_EM[2]:e_m, ID_EM[5]:e_e, ID_EM[3]:e_w, ID_EM[4]:e_u})
                st.success("✅ Carga publicada"); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            # Forzamos la descarga fresca del CSV (Hoja 6)
            url_choferes = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&cache={time.time()}"
            df_h = pd.read_csv(url_choferes).fillna("S/D")
            
            for _, r in df_h.iloc[::-1].iterrows():
                # Hoja 6: B=1:Origen, C=2:Destino, D=3:Equipo, E=4:WhatsApp
                h_orig, h_dest, h_equi, h_tel = r[1], r[2], r[3], r[4]
                
                if b_orig and b_orig.lower() not in str(h_orig).lower(): continue
                if b_dest and b_dest.lower() not in str(h_dest).lower(): continue

                txt_h = f"¡Hola! Vi tu camión disponible de {h_orig} a {h_dest} en Retorno Match 🚛\n¿Seguís disponible?"
                link_h = f"https://api.whatsapp.com/send?phone=549{h_tel}&text={urllib.parse.quote(txt_h)}"

                st.markdown(f"""
                    <div class="card-white" style="border-left-color: #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(h_orig).upper()} ➔ {str(h_dest).upper()}</p>
                            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                                <div class="label-style">⚙️ <b>Equipo:</b> {h_equi}</div>
                                <div class="label-style">📱 <b>Tel:</b> {h_tel}</div>
                            </div>
                        </div>
                        <a href="{link_h}" target="_blank" class="btn-tomar" style="background:#2ecc71">HABLAR CON CHOFER</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones nuevos...")

# --- PANEL ADMIN ---
with st.expander("🔐 PANEL ADMIN (Borrar)"):
    pw = st.text_input("Clave:", type="password")
    if pw == ADMIN_PASSWORD:
        st.write("Para borrar, buscá el número de fila en el Excel y eliminalo.")
        # Aquí podrías listar las filas si quisieras.

st.markdown("<br><p style='text-align:center; opacity:0.6; font-size:12px;'>© 2026 RETORNO MATCH - San Jorge</p>", unsafe_allow_html=True)
