import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# Contraseña para borrar cargas (Cambiála si querés)
ADMIN_PASSWORD = "admin" 

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450", "entry.1930562861", "entry.1064058502"]

st.set_page_config(page_title="RETORNO MATCH | Panel Admin", page_icon="🚛", layout="wide")

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab-list"] { display: flex; width: 100%; gap: 5px; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 10px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; text-align: center;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 20px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        border-left: 12px solid #3498db; color: #333;
    }
    .route-style { font-size: 22px; font-weight: 900; color: #1e3799 !important; margin-bottom: 10px; }
    .label-style { background: #f8f9fa; padding: 8px; border-radius: 10px; font-size: 14px; margin-bottom: 5px; color: #333; border: 1px solid #ddd; }
    .btn-tomar { background-color: #3498db; color: white !important; padding: 12px 25px; border-radius: 12px; text-decoration: none; font-weight: 900; }
    .admin-box { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin-top: 50px; border: 1px dashed white; }
    h1, h2, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_orig = st.text_input("🔍 ORIGEN:")
with c2: b_dest = st.text_input("🏁 DESTINO:")

t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# === PESTAÑA 1: CHOFERES ===
with t1:
    col_izq, col_der = st.columns([1, 2.2])
    with col_izq:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o, d, e, w = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Térmico"]), st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("¡Publicado!"); st.rerun()

    with col_der:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            # --- FILTRO DE ELIMINADAS ---
            if 'Estado' not in df.columns: df['Estado'] = 'Activo'
            df = df[df['Estado'] != 'Borrado']
            
            for i, r in df.iloc[::-1].iterrows():
                ret, ent, mer, tel, emp, urg = r[1], r[2], r[3], r[4], r[5], r[6]
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                msg_ws = f"¡Hola! Te contacto por Retorno Match 🚛\n\nVi tu carga disponible:\n📍 Origen: {ret}\n🏁 Destino: {ent}\n📦 Carga: {mer}\n🏢 Empresa: {emp}\n\n¿Sigue disponible?"
                link_ws = f"https://api.whatsapp.com/send?phone=549{tel}&text={urllib.parse.quote(msg_ws)}"
                
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
                        <a href="{link_ws}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.error("Error al cargar.")

# === PESTAÑA 2: EMPRESAS (SOBREVIVE IGUAL) ===
with t2:
    st.info("Pestaña de empresas activa.")

# === 🔐 PANEL DE ADMINISTRADOR (PARA BORRAR) ===
st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
st.markdown("### 🔐 Panel de Control (Solo Ignacio)")
pwd = st.text_input("Contraseña para gestionar cargas:", type="password")

if pwd == ADMIN_PASSWORD:
    st.warning("⚠️ ESTÁS EN MODO EDICIÓN. Si borrás una carga, dejará de ser visible para los choferes.")
    try:
        df_admin = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
        for index, row in df_admin.iloc[::-1].iterrows():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"🗑️ {row[1]} -> {row[2]} ({row[5]})")
            with c2:
                if st.button(f"BORRAR #{index}", key=f"btn_{index}"):
                    # Aquí la lógica: En un sistema real usaríamos una API para borrar.
                    # Por ahora, te doy el aviso para que sepas qué fila es en el Excel.
                    st.error(f"Fila #{index+2} marcada. ¡Borrala en el Excel para limpiar!")
    except: st.write("No hay cargas para gestionar.")
st.markdown("</div>", unsafe_allow_html=True)
