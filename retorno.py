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

# --- 2. SISTEMA ANTI-PAUSA Y SESIÓN ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "anuncios" not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"

# --- 3. CARGA DE DATOS CON BLINDAJE DE BORRADO ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de borrado potenciado por Ignacio Diaz
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

def calcular_distancia(o, d):
    try:
        p1 = next((p for p in COORDS_PROV if p in str(o).upper()), None)
        p2 = next((p for p in COORDS_PROV if p in str(d).upper()), None)
        if p1 and p2:
            la1, lo1 = COORDS_PROV[p1]; la2, lo2 = COORDS_PROV[p2]
            a = math.sin(math.radians(la2-la1)/2)**2 + math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(math.radians(lo2-lo1)/2)**2
            return f"📍 {int(12742 * math.asin(math.sqrt(a)))} km aprox."
    except: pass
    return ""

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card-white { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; position: relative; }
    .card-vip { background: #fff9e6; border: 2px solid #f1c40f; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-cosecha { background: #e8f5e9; border: 2px solid #2e7d32; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; min-height: 180px; }
    .card-bloqueada { background: rgba(0,0,0,0.6); border: 2px dashed #f1c40f; color: white; text-align: center; padding: 30px; border-radius: 15px; margin-bottom: 15px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
    .btn-del { background-color: #ff4b4b; color: white !important; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ACCESO EXCLUSIVO IGNACIO ---
with st.sidebar:
    st.title("🛡️ Panel de Control")
    with st.expander("MODO ADMINISTRADOR"):
        pin_input = st.text_input("Ingrese PIN:", type="password")
        if pin_input == ADMIN_PIN:
            st.session_state.admin_mode = True
            st.success("Acceso Ignacio Diaz Concedido")
            st.session_state.anuncios = st.text_area("Editar Radar:", st.session_state.anuncios)
            if st.button("LIMPIAR BASE DE DATOS"):
                st.cache_data.clear()
                st.rerun()
        else:
            st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT Acceso VIP:", "").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL
    if es_user_vip: st.info("SISTEMA VIP HABILITADO")

st.title("🚛 RETORNO MATCH VIP")
busqueda_libre = st.text_input("🔎 Buscar (Provincia, Empresa o Equipo):").upper()

# Radar con firma I.S.D
st.markdown(f'<div style="background:#e74c3c; padding:10px; border-radius:10px; text-align:center;"><marquee scrollamount="8"><b>{st.session_state.anuncios} -- I.S.D</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS DISPONIBLES", "🌾 ARRIME COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Publicar Carga")
        with st.form("f_ca", clear_on_submit=True):
            o = st.selectbox("Origen", list(COORDS_PROV.keys()), key="o1")
            d = st.selectbox("Destino", list(COORDS_PROV.keys()), key="d1")
            m, en, w = st.text_input("Mercadería"), st.text_input("Empresa"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": m, "entry.1930562861": en, "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ch_raw.empty:
            for idx, r in df_ch_raw.iterrows():
                if busqueda_libre in str(r).upper():
                    is_v = str(r.iloc[4]) in LISTA_VIPS_GLOBAL or str(r.iloc[5]) in LISTA_VIPS_GLOBAL
                    dist = calcular_distancia(r.iloc[1], r.iloc[2])
                    st.markdown(f"""<div class="{'card-vip' if is_v else 'card-white'}">
                    <span style="float:right; color:#777;">{dist}</span>
                    <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                    <b>EQUIPO:</b> {r.iloc[3]} | 📱 <b>TEL:</b> {ocultar_telefono(r.iloc[5])}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a>
                    </div>""", unsafe_allow_html=True)
                    if st.session_state.admin_mode:
                        if st.button(f"🗑️ BORRAR CHOFER #{idx}", key=f"d_ch_{idx}"):
                            requests.post(URL_CHOFERES_POST, data={"entry.1304806144": "BORRADO", "entry.1542650763": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Publicar Camión")
        with st.form("f_ch", clear_on_submit=True):
            o_p = st.selectbox("Desde", list(COORDS_PROV.keys()), key="o2")
            d_p = st.selectbox("Hacia", list(COORDS_PROV.keys()), key="d2")
            eq, cu, ws = st.text_input("Equipo"), st.text_input("CUIT"), st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_ca_f.iterrows():
                try:
                    minutos = (datetime.now() - pd.to_datetime(r.iloc[0], dayfirst=True)).total_seconds() / 60
                    if minutos < TIEMPO_EXCLUSIVO_MIN and not es_user_vip:
                        st.markdown(f'<div class="card-bloqueada">🔒 CARGA EXCLUSIVA VIP<br><small>Disponible en {int(TIEMPO_EXCLUSIVO_MIN-minutos)} min</small></div>', unsafe_allow_html=True)
                    elif busqueda_libre in str(r).upper():
                        st.markdown(f"""<div class="card-white"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                        <b>CARGA:</b> {r.iloc[3]} | 🏢 {r.iloc[5]} | 📱 {ocultar_telefono(r.iloc[4])}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a>
                        </div>""", unsafe_allow_html=True)
                        if st.session_state.admin_mode:
                            if st.button(f"🗑️ BORRAR CARGA #{idx}", key=f"d_ca_{idx}"):
                                requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                                st.cache_data.clear(); st.rerun()
                except: continue

# --- TAB 3: COSECHA ---
with tab3:
    st.subheader("🌾 ARRIME DE COSECHA")
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("f_arr", clear_on_submit=True):
            z, g, w_a = st.text_input("📍 Localidad"), st.text_input("Grano/Tarifa"), st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR ARRIME"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w_a})
                st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            df_a = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                if busqueda_libre in str(r).upper():
                    st.markdown(f"""<div class="card-cosecha"><div class="route-txt" style="color:#2e7d32;">📍 {r.iloc[2]}</div>
                    <b>INFO:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a>
                    </div>""", unsafe_allow_html=True)
                    if st.session_state.admin_mode:
                        if st.button(f"🗑️ BORRAR ARRIME #{idx}", key=f"d_ar_{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()

# --- FOOTER LEGAL ---
st.markdown(f"""
<div style="text-align: center; color: rgba(255,255,255,0.7); padding: 50px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)
