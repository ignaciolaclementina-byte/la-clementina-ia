import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ Y SUS LEGALES) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "ESCRIBE_AQUI_EL_GID_DE_LA_HOJA_VIP" # <-- Esto es lo único nuevo

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 

# --- 2. CARGA DE DATOS ---
@st.cache_data(ttl=15)
def cargar_datos_vip():
    try:
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
        # Lectura de VIPs desde la nube para que sea global
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}", header=None)
        vips = [str(x).strip().upper() for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), ["FLEMING"]

df_ch, df_ca, LISTA_VIPS = cargar_datos_vip()

# --- 3. ESTILOS (MANTENIENDO TU DISEÑO) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; }
    .card-white { background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6; border: 4px solid #f1c40f; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241,196,15,0.6); }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 65px; background-color: #2c3e50 !important; color: white !important; font-size: 18px; font-weight: 900; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- 4. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    return any(v in str(dato).upper() for v in LISTA_VIPS)

# --- 5. BÚSQUEDA ---
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", ["CUALQUIERA", "BUENOS AIRES", "CABA", "CORDOBA", "SANTA FE", "MENDOZA"]) # Simplificado por espacio
with c3: b_d = st.selectbox("🏁 DESTINO:", ["CUALQUIERA", "BUENOS AIRES", "CABA", "CORDOBA", "SANTA FE", "MENDOZA"])
with c4: b_e = st.selectbox("🚛 EQUIPO:", ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"])
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR"): st.cache_data.clear(); st.rerun()

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">🚛 FECHA: {b_fecha.strftime("%d/%m/%Y")} -- ⭐ ¡Membresías VIP Activas! -- Creado por Ignacio Diaz y sus legales.</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# --- TAB 1: EMPRESA BUSCA CAMION (MANTENIENDO 1, 2.2) ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_carga"):
            eo = st.text_input("Origen"); ed = st.text_input("Destino"); ec = st.text_input("Carga"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":eo,"entry.170847116":ed,"entry.576675281":ec,"entry.1930562861":en,"entry.466540450":ew})
                st.success("Publicado"); st.rerun()
    with col_r1:
        for _, r in df_ch.iterrows():
            try:
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    v = es_vip(r[4])
                    clase = "card-vip" if v else "card-white"
                    label = '<div class="vip-label">⭐ CHOFER VIP</div>' if v else ""
                    st.markdown(f'<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛:</b> {r[3]} | 🆔: {r[4]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Hola!" target="_blank" class="btn-wsp">💬 CONTACTAR</a></div>', unsafe_allow_html=True)
            except: continue

# --- TAB 2: CHOFER BUSCA CARGA (MANTENIENDO 1, 2.2) ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_camion"):
            o = st.text_input("Origen"); d = st.text_input("Destino"); e = st.text_input("Equipo"); cu = st.text_input("CUIT"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144":o,"entry.1519265625":d,"entry.597193898":e,"entry.1542650763":cu,"entry.1574172378":w})
                st.success("Publicado"); st.rerun()
    with col_r2:
        for _, r in df_ca.iterrows():
            try:
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    v = es_vip(r[4])
                    clase = "card-vip" if v else "card-white"
                    label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if v else ""
                    st.markdown(f'<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦:</b> {r[3]} | 🏢: {r[4]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Hola!" target="_blank" class="btn-wsp">💬 CONSULTAR</a></div>', unsafe_allow_html=True)
            except: continue

# --- 6. PANEL DE CONTROL (BLINDADO) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (IGNACIO DIAZ)"):
    if st.text_input("PIN Admin:", type="password") == ADMIN_PIN:
        # Botón para ir al Excel directo desde el celular
        url_excel = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}"
        st.markdown(f'<a href="{url_excel}" target="_blank" style="display:block; background:#f1c40f; color:black; text-align:center; padding:15px; border-radius:10px; font-weight:bold; text-decoration:none;">➕ CARGAR NUEVO VIP AL SISTEMA GLOBAL</a>', unsafe_allow_html=True)

st.markdown(f'<div class="legal-footer"><b>Creado por Ignacio Diaz y sus legales</b><br>© 2026 RETORNO MATCH VIP</div>', unsafe_allow_html=True)
