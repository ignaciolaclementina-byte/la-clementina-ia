import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.1064058502", "entry.466540450"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. LÓGICA DE APOYO ---
def obtener_color_urgencia(estado):
    est = str(estado).lower()
    if "hoy" in est: return "#FF4B4B", "🚨 SALE HOY"
    if "mañana" in est: return "#F1C40F", "⏳ SALE MAÑANA"
    if "apuro" in est: return "#2ECC71", "✅ SIN APURO"
    return "#3498DB", "📦 DISPONIBLE"

def detectar_pais_y_whatsapp(tel_sucio):
    num = "".join(filter(str.isdigit, str(tel_sucio)))
    if not num: return "🌐", ""
    bandera = "🇦🇷" if num.startswith("54") else "🌐"
    if len(num) <= 10: num = "549" + num
    return bandera, num

# --- 3. INTERFAZ Y ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 22px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .route-style { font-size: 22px; font-weight: 800; color: #1e3799 !important; margin-bottom: 10px; }
    /* CÁPSULAS MEJORADAS */
    .label-style { 
        background: #f8f9fa; padding: 6px 14px; border-radius: 10px; font-size: 13px; 
        color: #333; border: 1px solid #dee2e6; display: flex; align-items: center; gap: 8px; font-weight: 500;
    }
    .btn-tomar { 
        background-color: #3498db; color: white !important; padding: 15px 30px; 
        border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 16px;
        transition: 0.3s; display: inline-block;
    }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h1 style='font-size: 50px; font-weight: 900;'>🚛 RETORNO MATCH</h1></div>", unsafe_allow_html=True)

# --- BUSCADORES ---
with st.container():
    c_b1, c_b2 = st.columns(2)
    with c_b1: b_orig = st.text_input("📍 Buscar Origen:")
    with c_b2: b_dest = st.text_input("🏁 Buscar Destino:")

t1, t2 = st.tabs(["🚀 CHOFERES (Ver Cargas)", "🏢 EMPRESAS (Ver Camiones)"])

# === PESTAÑA CHOFERES ===
with t1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f1", clear_on_submit=True):
            o, d, e, w = st.text_input("📍 Mi Ubicación"), st.text_input("🏁 Destino deseado"), st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Térmico"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.balloons(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("No especificado")
            for _, r in df.iloc[::-1].iterrows():
                f, ret, ent, mer, emp, urg, tel = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                color, txt_urg = obtener_color_urgencia(urg)
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                msg = urllib.parse.quote(f"Hola! Vi tu carga en Retorno Match: {ret} -> {ent}. ¿Sigue disponible?")
                
                st.markdown(f"""
                    <div class="card-white" style="border-left: 12px solid {color};">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                                <div class="label-style" style="border-left: 4px solid {color};"><b>{txt_urg}</b></div>
                                <div class="label-style">📦 <b>Carga:</b> {mer}</div>
                                <div class="label-style">🏢 <b>Empresa:</b> {emp}</div>
                                <div class="label-style">{bandera} <b>Tel:</b> {tel}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Actualizando tablero...")

# === PESTAÑA EMPRESAS ===
with t2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 🏢 Publicar Nueva Carga")
        with st.form("f2", clear_on_submit=True):
            eo, ed, em, en = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Qué mercadería es?"), st.text_input("🏢 Nombre de Empresa")
            eu = st.selectbox("⏳ Urgencia", ["Sale hoy", "Sale mañana", "Sin apuro"])
            ew = st.text_input("📱 WhatsApp de contacto")
            if st.form_submit_button("PUBLICAR CARGA AHORA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:eu, ID_EM[5]:ew})
                st.balloons(); st.success("¡Carga publicada!"); time.sleep(1); st.rerun()
    with c2:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in dfh.iloc[::-1].iterrows():
                f, o, d, eq, tel = r[0], r[1], r[2], r[3], r[4]
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                st.markdown(f"""
                    <div class="card-white" style="border-left: 12px solid #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(o).upper()} ➔ {str(d).upper()}</p>
                            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                                <div class="label-style">⚙️ <b>Equipo:</b> {eq}</div>
                                <div class="label-style">{bandera} <b>WhatsApp:</b> {tel}</div>
                                <div class="label-style">🕒 <b>Visto:</b> {f}</div>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-tomar" style="background:#2ecc71">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# --- PIE DE PÁGINA ---
st.markdown("<br><hr><div style='color:white; text-align:center; opacity:0.6; font-size:12px;'>© 2026 RETORNO MATCH - Ignacio Diaz | San Jorge, Santa Fe</div>", unsafe_allow_html=True)
