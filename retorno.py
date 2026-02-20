import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

# --- 2. GESTIÓN DE ESTADO ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! Creado por Ignacio Diaz y sus legales."

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 3. ESTILOS BLINDADOS (CORREGIDOS PARA QUE SE VEAN BIEN) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075');
        background-size: cover; background-attachment: fixed;
    }
    .main-title {
        text-align: center; color: #f1c40f; font-size: 45px; font-weight: 900;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5); margin-bottom: 5px;
    }
    .sub-title {
        text-align: center; color: white; font-size: 18px; letter-spacing: 2px;
        margin-bottom: 30px; opacity: 0.8;
    }
    .radar-container {
        background: rgba(231, 76, 60, 0.95); color: white; padding: 12px; 
        border-radius: 10px; border: 1px solid #f1c40f; margin-bottom: 25px;
    }
    .card-vip {
        background: #fffdf5 !important; border: 2px solid #f1c40f !important;
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0px 5px 15px rgba(241, 196, 15, 0.2);
    }
    .card-standard {
        background: white !important; border-radius: 15px; padding: 20px;
        margin-bottom: 15px; border-left: 8px solid #3498db;
    }
    .vip-tag {
        background: #f1c40f; color: black; padding: 3px 10px; 
        border-radius: 5px; font-weight: bold; font-size: 12px;
    }
    .route-txt { font-size: 20px; font-weight: 800; color: #1e3799; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; text-align: center;
        padding: 10px; border-radius: 8px; display: block; text-decoration: none;
        font-weight: bold; margin-top: 10px;
    }
    .footer { text-align: center; color: #888; padding: 30px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 4. ENCABEZADO TEXTUAL (MÁS CONFIABLE QUE IMAGEN) ---
st.markdown('<div class="main-title">RETORNO MATCH</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">⭐ SERVICIO VIP ⭐</div>', unsafe_allow_html=True)

# --- 5. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

def es_vip(dato):
    lista = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista

# Carga de datos
try:
    df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch, df_ca = pd.DataFrame(), pd.DataFrame()

# --- 6. RADAR ---
st.markdown(f'<div class="radar-container"><marquee scrollamount="7">⭐ {st.session_state.anuncios} -- 🚛 Creado por Ignacio Diaz y sus legales.</marquee></div>', unsafe_allow_html=True)

# --- 7. FILTROS ---
c1, c2, c3 = st.columns(3)
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO:", ["CUALQUIERA"] + EQUIPOS)

st.markdown("<br>", unsafe_allow_html=True)
t1, t2 = st.tabs(["🚀 BUSCAR CAMIONES", "🏢 BUSCAR CARGAS"])

# PESTAÑA 1: CAMIONES (VIP PRIMERO)
with t1:
    if not df_ch.empty:
        df_ch['vip'] = df_ch.iloc[:, 5].apply(es_vip)
        # Filtramos por fecha hoy y ordenamos VIP arriba
        df_f = df_ch[df_ch.iloc[:,0].apply(es_hoy)].sort_values('vip', ascending=False)
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                clase = "card-vip" if r['vip'] else "card-standard"
                tag = '<span class="vip-tag">⭐ CHOFER VIP</span>' if r['vip'] else ""
                st.markdown(f'''<div class="{clase}">{tag}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                <b>EQUIPO:</b> {r[3]} | <b>CUIT:</b> {r[5]}<br>
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">💬 CONTACTAR AHORA</a></div>''', unsafe_allow_html=True)

# PESTAÑA 2: CARGAS (VIP PRIMERO)
with t2:
    if not df_ca.empty:
        df_ca['vip'] = df_ca.iloc[:, 5].apply(es_vip)
        df_f2 = df_ca[df_ca.iloc[:,0].apply(es_hoy)].sort_values('vip', ascending=False)
        for _, r in df_f2.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                clase = "card-vip" if r['vip'] else "card-standard"
                tag = '<span class="vip-tag">⭐ EMPRESA VIP</span>' if r['vip'] else ""
                st.markdown(f'''<div class="{clase}">{tag}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                <b>CARGA:</b> {r[3]} | <b>EMPRESA:</b> {r[5]}<br>
                <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">💬 CONSULTAR CARGA</a></div>''', unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
with st.expander("⚙️ ADMINISTRACIÓN"):
    st.session_state.anuncios = st.text_input("Mensaje Radar:", st.session_state.anuncios)
    st.session_state.socios_activos = st.text_area("Lista VIP (CUIT o Nombre):", st.session_state.socios_activos)
    if st.button("ACTUALIZAR"): st.rerun()

st.markdown('<div class="footer">Creado por Ignacio Diaz y sus legales. Prohibida su copia.</div>', unsafe_allow_html=True)
