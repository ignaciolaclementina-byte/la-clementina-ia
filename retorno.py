import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - FIRMA: I.S.D) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30 

COORDS_PROV = {
    "BUENOS AIRES": (-34.921, -57.954), "CABA": (-34.603, -58.381), "CATAMARCA": (-28.469, -65.785),
    "CHACO": (-27.451, -58.986), "CHUBUT": (-43.300, -65.102), "CORDOBA": (-31.413, -64.181),
    "CORRIENTES": (-27.469, -58.830), "ENTRE RIOS": (-31.733, -60.529), "FORMOSA": (-26.177, -58.178),
    "JUJUY": (-24.185, -65.299), "LA PAMPA": (-36.616, -64.283), "LA RIOJA": (-29.411, -66.850),
    "MENDOZA": (-32.889, -68.845), "MISIONES": (-27.367, -55.896), "NEUQUEN": (-38.951, -68.059),
    "RIO NEGRO": (-40.813, -62.996), "SALTA": (-24.785, -65.411), "SAN JUAN": (-31.537, -68.536),
    "SAN LUIS": (-33.295, -66.335), "SANTA CRUZ": (-51.622, -69.218), "SANTA FE": (-31.633, -60.700),
    "SANTIAGO DEL ESTERO": (-27.795, -64.263), "TIERRA DEL FUEGO": (-54.801, -68.303), "TUCUMAN": (-26.824, -65.222)
}

# --- 2. GESTIÓN DE SESIÓN ---
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "anuncios" not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        if not df_ca.empty:
            mask_b = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs = [re.search(r'REF:(.*)', str(cell)).group(1).strip() for row in df_ca[mask_b].values for cell in row if re.search(r'REF:(.*)', str(cell))]
            df_ca = df_ca[~mask_b]
            if refs:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs)]

        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. FUNCIONES CORE ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def calcular_km(o, d):
    try:
        p1, p2 = next((p for p in COORDS_PROV if p in str(o).upper()), None), next((p for p in COORDS_PROV if p in str(d).upper()), None)
        if p1 and p2:
            la1, lo1 = COORDS_PROV[p1]; la2, lo2 = COORDS_PROV[p2]
            a = math.sin(math.radians(la2-la1)/2)**2 + math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(math.radians(lo2-lo1)/2)**2
            return f"📍 {int(12742 * math.asin(math.sqrt(a)))} km"
    except: pass
    return ""

# --- 5. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
df_ch, df_ca, LISTA_VIPS = cargar_datos_seguros()

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; }
    .card-vip { background: #fff9e6; border: 2px solid #f1c40f; }
    .card-cosecha { background: #e8f5e9; border-left-color: #2e7d32; }
    .route { font-size: 18px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH VIP")

# Panel Superior
with st.container():
    c1, c2 = st.columns([1, 2])
    with c1:
        u_cuit = st.text_input("🔑 CUIT Acceso:", "").strip().replace(".0", "")
        if u_cuit in LISTA_VIPS: st.success("MODO VIP ACTIVO")
    with c2:
        f_txt = st.text_input("🔎 Búsqueda rápida:").upper()

# Radar de Anuncios FIRMA I.S.D
st.markdown(f'<div style="background:#e74c3c; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="7"><b>{st.session_state.anuncios} -- I.S.D</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TABLA CAMIONES ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Publicar Carga")
        with st.form("f1", clear_on_submit=True):
            o, d = st.selectbox("Origen", list(COORDS_PROV.keys())), st.selectbox("Destino", list(COORDS_PROV.keys()))
            ms, em, ws = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": ms, "entry.1930562861": em, "entry.466540450": ws})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ch.empty:
            for idx, r in df_ch.iterrows():
                if f_txt in str(r).upper():
                    is_v = str(r.iloc[4]) in LISTA_VIPS or str(r.iloc[5]) in LISTA_VIPS
                    st.markdown(f'<div class="card {"card-vip" if is_v else ""}"> <span style="float:right;">{calcular_km(r.iloc[1], r.iloc[2])}</span> <div class="route">{r.iloc[1]} ➔ {r.iloc[2]}</div> <b>EQUIPO:</b> {r.iloc[3]} | 📱 <b>TEL:</b> *******{str(r.iloc[5])[-4:]} <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">CONTACTAR</a> </div>', unsafe_allow_html=True)
                    if st.session_state.admin_mode and st.button(f"🗑️ BORRAR #{idx}", key=f"ch_{idx}"):
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": "BORRADO", "entry.1542650763": f"REF:{r.iloc[0]}"})
                        st.cache_data.clear(); st.rerun()

# --- TABLA CARGAS ---
with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Publicar Camión")
        with st.form("f2", clear_on_submit=True):
            o_c, d_c = st.selectbox("Origen ", list(COORDS_PROV.keys())), st.selectbox("Destino ", list(COORDS_PROV.keys()))
            eq_c, cuit_c, wsp_c = st.text_input("Equipo"), st.text_input("CUIT"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_c, "entry.1519265625": d_c, "entry.597193898": eq_c, "entry.1542650763": cuit_c, "entry.1574172378": wsp_c})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ca.empty:
            df_f = df_ca[~df_ca.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_f.iterrows():
                try:
                    mins = (datetime.now() - pd.to_datetime(r.iloc[0], dayfirst=True)).total_seconds() / 60
                    if mins < TIEMPO_EXCLUSIVO_MIN and u_cuit not in LISTA_VIPS:
                        st.markdown(f'<div class="card" style="background:#eee;">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-mins)} min)</div>', unsafe_allow_html=True)
                    elif f_txt in str(r).upper():
                        st.markdown(f'<div class="card"><div class="route">{r.iloc[1]} ➔ {r.iloc[2]}</div><b>CARGA:</b> {r.iloc[3]} | 🏢 {r.iloc[5]}<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)
                        if st.session_state.admin_mode and st.button(f"🗑️ BORRAR #{idx}", key=f"ca_{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()
                except: continue

# --- TABLA COSECHA ---
with tab3:
    st.subheader("🌾 SECCIÓN ESPECIAL ARRIME")
    col1, col2 = st.columns([1, 2])
    with col1:
        with st.form("f3", clear_on_submit=True):
            z, g, w = st.text_input("📍 Zona"), st.text_input("Grano/Tarifa"), st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with col2:
        if not df_ca.empty:
            df_a = df_ca[df_ca.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                if f_txt in str(r).upper():
                    st.markdown(f'<div class="card card-cosecha"><div class="route">📍 {r.iloc[2]}</div><b>DETALLE:</b> {r.iloc[3]} | 📱 *******{str(r.iloc[4])[-4:]}<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a></div>', unsafe_allow_html=True)
                    if st.session_state.admin_mode and st.button(f"🗑️ BORRAR #{idx}", key=f"ar_{idx}"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                        st.cache_data.clear(); st.rerun()

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; margin-top:50px;'><hr><b>I.S.D - 2026</b></div>", unsafe_allow_html=True)

# --- PANEL ADMIN ---
with st.sidebar:
    st.header("⚙️ ADMIN")
    pin = st.text_input("PIN:", type="password")
    if pin == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("AUTORIZADO")
        st.session_state.anuncios = st.text_area("Radar:", st.session_state.anuncios)
        if st.button("LIMPIAR DATOS"): st.cache_data.clear(); st.rerun()
    else: st.session_state.admin_mode = False
