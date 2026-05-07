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

# --- COORDENADAS PARA GEOLOCALIZACIÓN ---
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

# --- 2. SISTEMA DE SEGURIDAD Y CARGA ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Avanzado (Elimina registros y sus referencias)
        if not df_ca.empty:
            mask_b = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs = [re.search(r'REF:(.*)', str(cell)).group(1).strip() for row in df_ca[mask_b].values for cell in row if re.search(r'REF:(.*)', str(cell))]
            df_ca = df_ca[~mask_b]
            if refs:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs)]

        # Carga Lista VIP
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 3. FUNCIONES CORE ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def validar_cuit(cuit):
    c = "".join(filter(str.isdigit, str(cuit)))
    if len(c) != 11: return False
    m = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    v = 11 - (sum(int(c[i]) * m[i] for i in range(10)) % 11)
    return (0 if v == 11 else (9 if v == 10 else v)) == int(c[10])

def calcular_km(o, d):
    try:
        p1, p2 = next((p for p in COORDS_PROV if p in str(o).upper()), None), next((p for p in COORDS_PROV if p in str(d).upper()), None)
        if p1 and p2:
            la1, lo1 = COORDS_PROV[p1]; la2, lo2 = COORDS_PROV[p2]
            a = math.sin(math.radians(la2-la1)/2)**2 + math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(math.radians(lo2-lo1)/2)**2
            return f"📍 {int(12742 * math.asin(math.sqrt(a)))} km"
    except: pass
    return ""

# --- 4. DISEÑO VIP ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; color: white; }
    .card { background: white; color: #333; padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 10px solid #3498db; position: relative; }
    .card-vip { background: #fff9e6; border: 2px solid #f1c40f; }
    .card-cosecha { background: #e8f5e9; border-left-color: #2e7d32; }
    .badge-vip { background: #f1c40f; color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 10px; }
    .route { font-size: 18px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 5. LOGICA DE NAVEGACIÓN ---
df_ch, df_ca, LISTA_VIPS = cargar_datos_seguros()
ahora = datetime.now()

st.title("🚛 RETORNO MATCH VIP")

with st.sidebar:
    st.header("🔑 MI CUENTA")
    user_cuit = st.text_input("CUIT/ID Acceso:", "").strip().replace(".0", "")
    es_user_vip = user_cuit in LISTA_VIPS
    if es_user_vip: st.success("MODO VIP ACTIVO")
    
    st.divider()
    pin = st.text_input("PIN ADMIN:", type="password")
    st.session_state.admin = (pin == ADMIN_PIN)

# Filtros principales
col_f1, col_f2, col_f3 = st.columns(3)
f_orig = col_f1.selectbox("📍 Origen:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
f_dest = col_f2.selectbox("🏁 Destino:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
f_txt = col_f3.text_input("🔎 Buscar...").upper()

st.markdown(f'<div style="background:#e74c3c; padding:10px; border-radius:10px; text-align:center;"><marquee><b>Creado por Ignacio Diaz -- RETORNO MATCH SAN JORGE -- {ahora.strftime("%d/%m/%Y")}</b></marquee></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS DISPONIBLES", "🌾 ARRIME COSECHA"])

# --- TABLA CAMIONES ---
with t1:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Publicar Carga")
        with st.form("p1"):
            or_p = st.selectbox("Origen", list(COORDS_PROV.keys())); ds_p = st.selectbox("Destino", list(COORDS_PROV.keys()))
            ms = st.text_input("Carga/Mercadería"); em = st.text_input("Empresa"); ws = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": or_p, "entry.170847116": ds_p, "entry.576675281": ms, "entry.1930562861": em, "entry.466540450": ws})
                st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ch.empty:
            for _, r in df_ch.iterrows():
                try:
                    if (f_orig == "CUALQUIERA" or f_orig in str(r.iloc[1]).upper()) and (f_dest == "CUALQUIERA" or f_dest in str(r.iloc[2]).upper()) and (f_txt in str(r).upper()):
                        is_v = str(r.iloc[4]) in LISTA_VIPS or str(r.iloc[5]) in LISTA_VIPS
                        st.markdown(f"""<div class="card {'card-vip' if is_v else ''}">
                        <span style="float:right;">{calcular_km(r.iloc[1], r.iloc[2])}</span>
                        { '<span class="badge-vip">⭐ VIP</span>' if is_v else '' }
                        <div class="route">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                        <b>EQUIPO:</b> {r.iloc[3]} | 📱 <b>TEL:</b> *******{str(r.iloc[5])[-4:]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[5])}" class="btn-wsp">ENVIAR PROPUESTA</a>
                        </div>""", unsafe_allow_html=True)
                except: continue

# --- TABLA CARGAS ---
with t2:
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Publicar Camión")
        with st.form("p2"):
            o = st.selectbox("Desde", list(COORDS_PROV.keys())); d = st.selectbox("Hacia", list(COORDS_PROV.keys()))
            eq = st.text_input("Equipo "); cuit = st.text_input("CUIT "); wsp = st.text_input("WhatsApp ")
            if st.form_submit_button("SUBIR CAMIÓN"):
                if validar_cuit(cuit):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": eq, "entry.1542650763": cuit, "entry.1574172378": wsp})
                    st.cache_data.clear(); st.rerun()
                else: st.error("CUIT INVÁLIDO")
    with c2:
        if not df_ca.empty:
            df_ca_f = df_ca[~df_ca.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for _, r in df_ca_f.iterrows():
                try:
                    mins = (datetime.now() - pd.to_datetime(r.iloc[0], dayfirst=True)).total_seconds() / 60
                    if mins < TIEMPO_EXCLUSIVO_MIN and not es_user_vip:
                        st.markdown(f'<div class="card" style="text-align:center; background:#eee;">🔒 EXCLUSIVO VIP ({int(TIEMPO_EXCLUSIVO_MIN-mins)} min rest.)</div>', unsafe_allow_html=True)
                    elif (f_orig == "CUALQUIERA" or f_orig in str(r.iloc[1]).upper()) and (f_dest == "CUALQUIERA" or f_dest in str(r.iloc[2]).upper()) and (f_txt in str(r).upper()):
                        st.markdown(f"""<div class="card"><div class="route">{r.iloc[1]} ➔ {r.iloc[2]}</div>
                        <b>CARGA:</b> {r.iloc[3]} | 🏢 {r.iloc[5]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp">CONSULTAR</a>
                        </div>""", unsafe_allow_html=True)
                except: continue

# --- TABLA COSECHA ---
with t3:
    st.subheader("🌾 SECCIÓN ESPECIAL ARRIME")
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("p3"):
            z = st.text_input("📍 Zona/Localidad"); g = st.text_input("Grano/Detalle"); w = st.text_input("WhatsApp  ")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z, "entry.576675281": g, "entry.1930562861": "COSECHA", "entry.466540450": w})
                st.cache_data.clear(); st.rerun()
    with c2:
        if not df_ca.empty:
            df_a = df_ca[df_ca.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for idx, r in df_a.iterrows():
                try:
                    st.markdown(f"""<div class="card card-cosecha"><div class="route">📍 {r.iloc[2]}</div>
                    <b>DETALLE:</b> {r.iloc[3]} | 📱 *******{str(r.iloc[4])[-4:]}
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" class="btn-wsp" style="background:#2e7d32;">CONTACTAR</a>
                    </div>""", unsafe_allow_html=True)
                    if st.session_state.admin:
                        if st.button(f"🗑️ BORRAR #{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r.iloc[0]}"})
                            st.cache_data.clear(); st.rerun()
                except: continue

# --- FOOTER ---
st.markdown(f"<div style='text-align:center; margin-top:50px;'><hr><b>Creado por Ignacio Diaz - 2026</b><br>Prohibida su reproducción total o parcial.</div>", unsafe_allow_html=True)
