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

# Diccionario de Pueblos y Localidades Estratégicas (Mejora solicitada)
LOC_ZONA = {
    "SELECCIONAR": (0,0),
    "SAN JORGE": (-31.896, -61.859),
    "SASTRE": (-31.765, -61.828),
    "EL TREBOL": (-32.198, -61.701),
    "CARLOS PELLEGRINI": (-32.053, -61.789),
    "CAÑADA ROSQUIN": (-32.050, -61.411),
    "PIAMONTE": (-31.988, -61.986),
    "MARIA SUSANA": (-32.268, -61.908),
    "LANDETA": (-31.912, -62.083),
    "CRISPI": (-31.711, -61.921),
    "LAS PETACAS": (-31.841, -62.046),
    "CASTELAR": (-31.668, -62.029),
    "SAN FRANCISCO": (-31.424, -62.084),
    "ROSARIO (PUERTOS)": (-32.946, -60.639),
    "SANTA FE": (-31.633, -60.700),
    "PUERTO GRAL SAN MARTIN": (-32.716, -60.733),
    "TIMBUES": (-32.666, -60.781),
    "CORDOBA CAP": (-31.413, -64.181)
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

def calcular_distancia(origen, destino):
    lat1, lon1 = LOC_ZONA.get(origen, (0,0))
    lat2, lon2 = LOC_ZONA.get(destino, (0,0))
    if lat1 == 0 or lat2 == 0: return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card-white { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-urgente { background: #fff1f1; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border: 3px solid #ff4b4b; animation: pulse 2s infinite; }
    .card-vip { background: #fff9e6; border: 2px solid #f1c40f; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-cosecha { background: #e8f5e9; border: 2px solid #2e7d32; color: #1b5e20; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    .card-bloqueada { background: rgba(0,0,0,0.7); border: 2px dashed #f1c40f; color: white; text-align: center; padding: 30px; border-radius: 15px; backdrop-filter: blur(5px); }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; transition: 0.3s; }
    .btn-wsp:hover { background: #128C7E; transform: scale(1.02); }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(255, 75, 75, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); } }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: PANEL EXCLUSIVO IGNACIO DIAZ ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.title("🛡️ Gestión Central")
    pin_input = st.text_input("PIN de Administrador:", type="password")
    
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios = st.text_area("📢 Radar de Mensajes:", st.session_state.anuncios)
        if st.button("♻️ Sincronizar Base de Datos"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.session_state.admin_mode = False

    st.divider()
    user_cuit = st.text_input("🔑 CUIT de Acceso VIP:", placeholder="Ingrese su CUIT").strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

# --- CABECERA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f'<div style="background:#e74c3c; padding:12px; border-radius:12px; text-align:center;"><marquee scrollamount="8"><b>{st.session_state.anuncios} -- I.S.D</b></marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 CALCULADOR"])

# --- TAB 1: CAMIONES ---
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            st.markdown("### 📝 Registrar Camión")
            with st.form("f_ch", clear_on_submit=True):
                o_p = st.selectbox("Origen", list(LOC_ZONA.keys()), key="o2")
                d_p = st.selectbox("Destino", list(LOC_ZONA.keys()), key="d2")
                eq = st.text_input("Equipo")
                cu = st.text_input("CUIT")
                ws = st.text_input("WhatsApp")
                if st.form_submit_button("🚀 PUBLICAR"):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o_p, "entry.1519265625": d_p, "entry.597193898": eq, "entry.1542650763": cu, "entry.1574172378": ws})
                    st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ch_raw.empty:
            for idx, r in df_ch_raw.iterrows():
                is_v = str(r.iloc[4]) in LISTA_VIPS_GLOBAL
                st.markdown(f"""<div class="{'card-vip' if is_v else 'card-white'}">
                <span class="route-txt">📍 {r.iloc[1]} ➔ {r.iloc[2]}</span><br>
                <b>EQUIPO:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}&text=Consulta%20Camion" class="btn-wsp">OFERTAR CARGA</a>
                </div>""", unsafe_allow_html=True)
                if st.session_state.admin_mode:
                    if st.button(f"🗑️ Borrar Camión {idx}"):
                        requests.post(URL_CHOFERES_POST, data={"entry.1304806144": "BORRADO", "entry.1542650763": f"REF:{r.iloc[0]}"})
                        st.cache_data.clear(); st.rerun()

# --- TAB 2: CARGAS ---
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.form("f_ca", clear_on_submit=True):
                o = st.selectbox("Origen", list(LOC_ZONA.keys()), key="o1")
                d = st.selectbox("Destino", list(LOC_ZONA.keys()), key="d1")
                m = st.text_input("Mercadería")
                en = st.text_input("Empresa")
                w = st.text_input("WhatsApp")
                urg = st.checkbox("🚨 URGENTE")
                if st.form_submit_button("💼 PUBLICAR CARGA"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": o, "entry.170847116": d, "entry.576675281": f"⚠️URG {m}" if urg else m, "entry.1930562861": en, "entry.466540450": w})
                    st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_ca_f.iterrows():
                es_u = "URG" in str(r.iloc[3]).upper()
                clase = "card-urgente" if es_u else "card-white"
                st.markdown(f"""<div class="{clase}">
                <div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                📦 {r.iloc[3]} | 🏢 {r.iloc[5]} | 📱 {ocultar_telefono(r.iloc[4])}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}&text=Carga%20{r.iloc[1]}" class="btn-wsp">SOLICITAR VIAJE</a>
                </div>""", unsafe_allow_html=True)
                if st.session_state.admin_mode:
                    if st.button(f"🗑️ Borrar Carga {idx}"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                        st.cache_data.clear(); st.rerun()

# --- TAB 3: COSECHA ---
with tab3:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.form("f_arr", clear_on_submit=True):
                z = st.selectbox("Localidad", list(LOC_ZONA.keys()), key="z1")
                g = st.text_input("Detalle Arrime")
                w_a = st.text_input("WhatsApp")
                if st.form_submit_button("🌾 SUBIR ARRIME"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w_a})
                    st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca_raw.empty:
            df_a = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                st.markdown(f"""<div class="card-cosecha">
                <div style="font-weight:900;">📍 ZONA: {r.iloc[2]}</div>
                {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a>
                </div>""", unsafe_allow_html=True)

# --- TAB 4: CALCULADOR CON PUEBLOS ---
with tab4:
    st.subheader("📊 Estimador de Fletes Local (Pueblo a Pueblo)")
    col_c1, col_c2 = st.columns([1, 1])
    with col_c1:
        origen_p = st.selectbox("📍 Salida", list(LOC_ZONA.keys()), key="p_ori")
        destino_p = st.selectbox("🏁 Llegada", list(LOC_ZONA.keys()), key="p_des")
        tarifa = st.number_input("💰 Tarifa base por KM ($)", value=2200, step=100)
    with col_c2:
        distancia_km = calcular_distancia(origen_p, destino_p)
        if distancia_km > 0:
            dist_real = distancia_km * 1.20 # Factor de ruta real 20%
            costo_total = dist_real * tarifa
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; border-left:8px solid #2ecc71;">
                <h3 style="margin:0; color:#2ecc71;">{dist_real:.1f} KM</h3>
                <p style="font-size:22px;">Flete: <b>${costo_total:,.0f}</b></p>
            </div>
            """, unsafe_allow_html=True)
            msg_w = f"Consulta Tarifa: {origen_p} a {destino_p} ({dist_real:.1f}km). Est: ${costo_total:,.0f}"
            st.markdown(f'<a href="https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg_w)}" class="btn-wsp">RESERVAR VIAJE</a>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; margin-top:50px;'><b>Creado por Ignacio Diaz - 2026</b></div>", unsafe_allow_html=True)
