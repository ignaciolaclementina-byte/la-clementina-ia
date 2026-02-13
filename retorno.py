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
# Orden corregido según tu link: Origen, Destino, Mercadería, Empresa, Urgencia, WhatsApp
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.1930562861", "entry.1064058502", "entry.466540450"]

st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# --- 2. FUNCIONES DE APOYO ---
def obtener_estilo_urgencia(estado):
    est = str(estado).lower()
    if "hoy" in est:
        return {"color": "#FF0000", "txt": "🚨 SALE HOY (URGENTE)"}
    elif "mañana" in est:
        return {"color": "#F1C40F", "txt": "⏳ SALE MAÑANA"}
    elif "apuro" in est:
        return {"color": "#2ECC71", "txt": "✅ SIN APURO"}
    return {"color": "#3498DB", "txt": "📦 DISPONIBLE"}

def detectar_pais_y_whatsapp(tel_sucio):
    num = "".join(filter(str.isdigit, str(tel_sucio)))
    if not num: return "🌐", ""
    if num.startswith("54"): bandera = "🇦🇷"
    elif num.startswith("598"): bandera = "🇺🇾"
    elif num.startswith("55"): bandera = "🇧🇷"
    else: bandera = "🌐"
    if len(num) <= 10: num = "549" + num
    return bandera, num

# --- 3. ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0.75)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.4); border-top: 5px solid #eee;
    }
    .route-style { font-size: 22px; font-weight: 800; color: #1e3799 !important; margin: 0; }
    .label-style { background: #f1f2f6; padding: 6px 12px; border-radius: 8px; font-size: 13px; color: #2f3542; font-weight: 600; display: flex; align-items: center; gap: 5px; }
    .urgencia-tag { font-weight: 900; font-size: 12px; padding: 4px 8px; border-radius: 4px; color: white; }
    .btn-tomar { background-color: #3498db; color: white !important; padding: 14px 28px; border-radius: 12px; text-decoration: none; font-weight: bold; font-size: 16px; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div style='text-align:center;'><h1 style='font-size: 50px; font-weight: 900;'>🚛 RETORNO MATCH</h1></div>", unsafe_allow_html=True)

# --- 4. BUSCADORES ---
with st.container():
    c_b1, c_b2 = st.columns(2)
    with c_b1: b_orig = st.text_input("🔍 Origen:")
    with c_b2: b_dest = st.text_input("🔍 Destino:")

t1, t2 = st.tabs(["🚀 CHOFERES", "🏢 EMPRESAS"])

# === PESTAÑA 1: CHOFERES (Ven Cargas) ===
with t1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("f_ch", clear_on_submit=True):
            o, d, e, w = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:w})
                st.balloons()
                st.success("✨ ¡PUBLICADO CON ÉXITO! Ya figurás en la lista.")
                time.sleep(2); st.rerun()
    with c2:
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("S/D")
            for _, r in df.iloc[::-1].iterrows():
                # Columnas: Fecha, Origen, Destino, Carga, Empresa, Urgencia, Tel
                f, ret, ent, mer, emp, urg, tel = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
                if b_orig and b_orig.lower() not in str(ret).lower(): continue
                if b_dest and b_dest.lower() not in str(ent).lower(): continue

                info_urg = obtener_estilo_urgencia(urg)
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                msg = urllib.parse.quote(f"Hola! Vi tu carga en Retorno Match: {ret}->{ent}. ¿Sigue disponible?")
                
                st.markdown(f"""
                    <div class="card-white" style="border-left: 12px solid {info_urg['color']};">
                        <div>
                            <p class="route-style">📍 {str(ret).upper()} ➔ {str(ent).upper()}</p>
                            <div style="margin-top:10px; display: flex; flex-wrap: wrap; gap: 8px;">
                                <span class="urgencia-tag" style="background: {info_urg['color']};">{info_urg['txt']}</span>
                                <span class="label-style">📦 {mer}</span>
                                <span class="label-style">🏢 {emp}</span>
                                <span class="label-style">{bandera} {tel}</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}&text={msg}" target="_blank" class="btn-tomar">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# === PESTAÑA 2: EMPRESAS (Ven Camiones) ===
with t2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("### 🏢 Publicar Nueva Carga")
        with st.form("f_em", clear_on_submit=True):
            eo, ed, em, en = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega"), st.text_input("📦 Mercadería"), st.text_input("🏢 Empresa")
            eu = st.selectbox("⏳ ¿Cuándo carga?", ["Sale hoy", "Sale mañana", "Sin apuro"])
            ew = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:en, ID_EM[4]:eu, ID_EM[5]:ew})
                st.toast("Carga publicada correctamente", icon="✅")
                st.success("🚀 ¡CARGA PUBLICADA! Los choferes ya pueden verla.")
                time.sleep(2); st.rerun()
    with c2:
        try:
            dfh = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("S/D")
            for _, r in dfh.iloc[::-1].iterrows():
                f, o, d, eq, tel = r[0], r[1], r[2], r[3], r[4]
                bandera, t_final = detectar_pais_y_whatsapp(tel)
                st.markdown(f"""
                    <div class="card-white" style="border-left: 8px solid #2ecc71;">
                        <div>
                            <p class="route-style">🚛 {str(o).upper()} ➔ {str(d).upper()}</p>
                            <div style="margin-top:8px; display: flex; gap: 10px;">
                                <span class="label-style">⚙️ {eq}</span>
                                <span class="label-style">{bandera} {tel}</span>
                            </div>
                        </div>
                        <a href="https://api.whatsapp.com/send?phone={t_final}" target="_blank" class="btn-tomar" style="background:#2ecc71">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando...")

# --- PIE DE PÁGINA ---
st.markdown(f"<div class='footer-text'>© {datetime.now().year} RETORNO MATCH - Ignacio Diaz</div>", unsafe_allow_html=True)
