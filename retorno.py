import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30  
WSP_VENTAS_VIP = "5493401525621"

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

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card-white { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; }
    .card-urgente { background: #fff1f1; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 3px solid #ff4b4b; animation: pulse 2s infinite; }
    .card-vip { background: #fff9e6; border: 2px solid #f1c40f; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-cosecha { background: #e8f5e9; border: 2px solid #2e7d32; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-bloqueada { background: rgba(0,0,0,0.6); border: 2px dashed #f1c40f; color: white; text-align: center; padding: 30px; border-radius: 15px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: PANEL EXCLUSIVO IGNACIO DIAZ ---
with st.sidebar:
    st.title("🛡️ Acceso Ignacio")
    pin_input = st.text_input("Ingresar PIN para Modificar:", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("SISTEMA DESBLOQUEADO")
        st.session_state.anuncios = st.text_area("Radar:", st.session_state.anuncios)
        if st.button("♻️ Actualizar Todo"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT VIP:", "").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

st.title("🚛 RETORNO MATCH VIP")
busqueda_libre = st.text_input("🔎 Filtrar por ciudad o empresa:").upper()

# Radar
st.markdown(f'<div style="background:#e74c3c; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="8"><b>{st.session_state.anuncios} -- I.S.D</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.subheader("📝 Nueva Carga")
            with st.form("f_ca", clear_on_submit=True):
                o = st.selectbox("Origen", list(COORDS_PROV.keys()), key="o1")
                d = st.selectbox("Destino", list(COORDS_PROV.keys()), key="d1")
                m, en, w = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
                urg = st.checkbox("🚨 ¿ES URGENTE?")
                if st.form_submit_button("PUBLICAR"):
                    m_final = f"⚠️URGENTE: {m}" if urg else m
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m_final, "entry.1930562861": en, "entry.466540450": w})
                    st.cache_data.clear(); st.rerun()
        else:
            st.markdown('<div class="admin-only-msg" style="background:#34495e; color:#f1c40f; padding:15px; border-radius:10px; text-align:center;">🔒 Formulario restringido.</div>', unsafe_allow_html=True)
    
    with c2:
        if not df_ch_raw.empty:
            for idx, r in df_ch_raw.iterrows():
                if busqueda_libre in str(r).upper():
                    is_v = str(r.iloc[4]) in LISTA_VIPS_GLOBAL or str(r.iloc[5]) in LISTA_VIPS_GLOBAL
                    st.markdown(f"""<div class="{'card-vip' if is_v else 'card-white'}">
                    <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                    <b>EQUIPO:</b> {r.iloc[3]} | 📱 <b>TEL:</b> {ocultar_telefono(r.iloc[5])}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a>
                    </div>""", unsafe_allow_html=True)
                    if st.session_state.admin_mode:
                        if st.button(f"🗑️ ELIMINAR #{idx}", key=f"d_ch_{idx}"):
                            requests.post(URL_CHOFERES_POST, data={"entry.1304806144": "BORRADO", "entry.1542650763": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.subheader("🚛 Nuevo Camión")
            with st.form("f_ch", clear_on_submit=True):
                o_p = st.selectbox("Desde", list(COORDS_PROV.keys()), key="o2")
                d_p = st.selectbox("Hacia", list(COORDS_PROV.keys()), key="d2")
                eq, cu, ws = st.text_input("Equipo"), st.text_input("CUIT"), st.text_input("WhatsApp")
                if st.form_submit_button("PUBLICAR"):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                    st.cache_data.clear(); st.rerun()
        else:
            st.markdown('<div class="admin-only-msg" style="background:#34495e; color:#f1c40f; padding:15px; border-radius:10px; text-align:center;">🔒 Formulario restringido.</div>', unsafe_allow_html=True)
    
    with c2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_ca_f.iterrows():
                try:
                    es_u = "URGENTE" in str(r.iloc[3]).upper()
                    minutos = (datetime.now() - pd.to_datetime(r.iloc[0], dayfirst=True)).total_seconds() / 60
                    if minutos < TIEMPO_EXCLUSIVO_MIN and not es_user_vip:
                        st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-minutos)} min)</div>', unsafe_allow_html=True)
                    elif busqueda_libre in str(r).upper():
                        clase = "card-urgente" if es_u else "card-white"
                        st.markdown(f"""<div class="{clase}"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                        <b>CARGA:</b> {r.iloc[3]} | 🏢 {r.iloc[5]} | 📱 {ocultar_telefono(r.iloc[4])}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a>
                        </div>""", unsafe_allow_html=True)
                        if st.session_state.admin_mode:
                            if st.button(f"🗑️ ELIMINAR #{idx}", key=f"d_ca_{idx}"):
                                requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                                st.cache_data.clear(); st.rerun()
                except: continue

# --- TAB 3: COSECHA ---
with tab3:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.subheader("🌾 Publicar Arrime")
            with st.form("f_arr", clear_on_submit=True):
                z, g, w_a = st.text_input("📍 Localidad"), st.text_input("Detalle"), st.text_input("WhatsApp")
                urg_a = st.checkbox("🚨 ¿URGENTE?")
                if st.form_submit_button("SUBIR"):
                    g_final = f"⚠️URGENTE: {g}" if urg_a else g
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g_final, "entry.1930562861": "COSECHA", "entry.466540450": w_a})
                    st.cache_data.clear(); st.rerun()
        else:
            st.markdown('<div class="admin-only-msg" style="background:#34495e; color:#f1c40f; padding:15px; border-radius:10px; text-align:center;">🔒 Formulario restringido.</div>', unsafe_allow_html=True)
    
    with c2:
        if not df_ca_raw.empty:
            df_a = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                if busqueda_libre in str(r).upper():
                    es_u_a = "URGENTE" in str(r.iloc[3]).upper()
                    estilo = "border: 4px solid red; background: #fff5f5;" if es_u_a else ""
                    st.markdown(f"""<div class="card-cosecha" style="{estilo}"><div class="route-txt" style="color:#2e7d32;">📍 {r.iloc[2]}</div>
                    <b>INFO:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a>
                    </div>""", unsafe_allow_html=True)
                    if st.session_state.admin_mode:
                        if st.button(f"🗑️ ELIMINAR #{idx}", key=f"d_ar_{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; margin-top:50px;'><hr><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
