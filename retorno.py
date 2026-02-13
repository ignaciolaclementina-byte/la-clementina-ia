import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# URLs de Google Forms
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.466540450"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. LÓGICA DE DETECCIÓN DE PAÍS Y BANDERA (ACTUALIZADA) ---
def detectar_pais_y_whatsapp(tel_sucio):
    num = "".join(filter(str.isdigit, str(tel_sucio)))
    if not num: return "🌐", ""

    # Detección por prefijo internacional
    if num.startswith("54"): 
        return "🇦🇷", num
    elif num.startswith("598"): 
        return "🇺🇾", num
    elif num.startswith("55"): 
        return "🇧🇷", num
    elif num.startswith("56"): 
        return "🇨🇱", num
    elif num.startswith("595"): 
        return "🇵🇾", num
    elif num.startswith("591"): 
        return "🇧🇴", num
    
    # Si el número es corto (local Argentina sin 54), asumimos AR y agregamos 549
    if len(num) <= 10:
        return "🇦🇷", "549" + num
    
    return "🌐", num

# --- 3. ESTILOS VISUALES (TU INTERFAZ DE DEPÓSITOS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .route-style { font-size: 20px; font-weight: 800; color: #1e3799 !important; margin: 0; }
    .label-style { background: #f1f2f6; padding: 5px 12px; border-radius: 8px; font-size: 14px; color: #2f3542; border: 1px solid #dcdde1; display: flex; align-items: center; gap: 6px; }
    .btn-blue { background-color: #3498db; color: white !important; padding: 12px 24px; border-radius: 12px; text-decoration: none; font-weight: bold; }
    .btn-green { background-color: #2ecc71; color: white !important; padding: 12px 24px; border-radius: 12px; text-decoration: none; font-weight: bold; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_24hs(df):
    try:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        limite = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= limite].copy()
    except: return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 50px; font-weight: 900;'>🚛 RETORNO MATCH</h1><p style='font-size: 20px; letter-spacing: 2px;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# === PESTAÑA 1: VISTA CHOFER ===
with t1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o, d = st.text_input("📍 Origen"), st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            w = st.text_input("📱 WhatsApp (Ej: 3406...)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.success("✅ Publicado"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 📦 Cargas Disponibles (Últimas 24hs)")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df = filtrar_24hs(df)
            for _, r in df.iloc[::-1].iterrows():
                f, ret, ent, mer, tel, emp = r[0], r[1], r[2], r[3], r[4], r[5]
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                st.markdown(f"""
                    <div class="card-white" style="border-left: 8px solid #3498db;">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="margin-top:8px; display: flex; flex-wrap: wrap; gap: 10px;">
                                <span class="label-style">📦 Carga: {mer}</span>
                                <span class="label-style">🏢 Empresa: {emp if pd.notna(emp) else 'S/D'}</span>
                                <span class="label-style">{bandera} Tel: {tel}</span>
                                <span class="label-style">🕒 {f.strftime('%H:%M')} hs</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-blue">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# === PESTAÑA 2: VISTA EMPRESA ===
with t2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 🏢 Publicar Nueva Carga")
        with st.form("f2", clear_on_submit=True):
            eo, ed = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega")
            em, en = st.text_input("📦 Mercadería"), st.text_input("🏢 Empresa")
            ew = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:ew})
                st.success("✅ Publicado"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 🚛 Camiones Disponibles (Últimas 24hs)")
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            dfh = filtrar_24hs(dfh)
            for _, r in dfh.iloc[::-1].iterrows():
                f, o, d, eq, tel = r[0], r[1], r[2], r[3], r[4]
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                st.markdown(f"""
                    <div class="card-white" style="border-left: 8px solid #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(o).upper()} ➔ {str(d).upper()}</p>
                            <div style="margin-top:8px; display: flex; flex-wrap: wrap; gap: 10px;">
                                <span class="label-style">⚙️ Equipo: {eq}</span>
                                <span class="label-style">{bandera} Tel: {tel}</span>
                                <span class="label-style">🕒 {f.strftime('%H:%M')} hs</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-green">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")
