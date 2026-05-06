import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30  

# --- 2. CARGA DE DATOS SEGUROS CON FILTRO DE BORRADO ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de borrado (Ignacio Diaz)
        if not df_ca.empty:
            mask_borrado = (df_ca.iloc[:, 0].astype(str).str.upper() == 'BORRADO')
            refs_borradas = []
            for _, f in df_ca[mask_borrado].iterrows():
                m = re.search(r'REF:(.*)', str(f.iloc[2]))
                if m: refs_borradas.append(m.group(1).strip())
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips
    except Exception:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- FUNCIONES AUXILIARES ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos(ts_str):
    try:
        ts = pd.to_datetime(ts_str, dayfirst=True, errors='coerce')
        return (ahora - ts).total_seconds() / 60
    except: return 999

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not clean: return "549"
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_tel(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 3. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #111; color: white; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 15px; margin-bottom: 10px; }
    .card-carga { background: #f0fff4 !important; border-left: 10px solid #2ecc71 !important; color: #333; padding: 15px; margin-bottom: 10px; }
    .route-txt { font-size: 18px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH VIP")

cuit = st.text_input("🔑 CUIT VIP:").strip()
es_usuario_vip = cuit.upper() in LISTA_VIPS_GLOBAL

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "SANTA FE", "CORDOBA", "ENTRE RIOS"] # Simplificado para el ejemplo

t1, t2, t3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

# --- TAB 1: CAMIONES ---
with t1:
    if not df_ch_raw.empty:
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]
        for _, r in df_f.iterrows():
            st.markdown(f'<div style="background:white; color:black; padding:10px; margin-bottom:5px; border-radius:5px;"><b>{r.iloc[1]} ➔ {r.iloc[2]}</b><br>{r.iloc[3]}</div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with t2:
    if not df_ca_raw.empty:
        # Filtrar para que no aparezcan las de Arrime aquí
        df_ca_std = df_ca_raw[~df_ca_raw.iloc[:, 1].str.contains("ARRIME", na=False)]
        for _, r in df_ca_std.iterrows():
            minutos = obtener_minutos(r.iloc[0])
            if minutos < TIEMPO_EXCLUSIVO_MIN and not es_usuario_vip:
                st.lock("Carga Exclusiva VIP")
            else:
                st.markdown(f'<div class="card-carga"><div class="route-txt">{r.iloc[1]} ➔ {r.iloc[2]}</div>{r.iloc[3]} | 🏢 {r.iloc[4]}</div>', unsafe_allow_html=True)

# --- TAB 3: COSECHA (SOLUCIÓN AL ERROR DE LA IMAGEN) ---
with t3:
    st.markdown("<h3 style='color:#f1c40f;'>🌾 PUBLICACIONES DE ARRIME</h3>", unsafe_allow_html=True)
    
    # Formulario para publicar
    with st.expander("➕ PUBLICAR NUEVO ARRIME"):
        with st.form("f_arrime"):
            z = st.text_input("Zona")
            d = st.text_input("Grano/Detalle")
            w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA",
                    "entry.170847116": z,
                    "entry.576675281": d,
                    "entry.1930562861": "COSECHA",
                    "entry.466540450": w
                })
                st.cache_data.clear()
                st.rerun()

    # Visualización (Aquí se corrigió el KeyError de image_83a3ba.jpg)
    if not df_ca_raw.empty:
        df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].str.contains("ARRIME", na=False)]
        
        for i, (idx, r) in enumerate(df_arr.iterrows()):
            # USAMOS .iloc PARA EVITAR EL KEYERROR
            zona = r.iloc[2]
            detalle = r.iloc[3]
            telefono = r.iloc[5] # Columna del WhatsApp
            
            link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(telefono)}"
            
            st.markdown(f'''
                <div class="card-cosecha">
                    <div class="route-txt" style="color:#2e7d32;">📍 {zona}</div>
                    <b>{detalle}</b> | 📱 {ocultar_tel(telefono)}<br>
                    <a href="{link_wsp}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">CONTACTAR</a>
                </div>
            ''', unsafe_allow_html=True)

st.markdown("<br><hr><center>Creado por Ignacio Diaz</center>", unsafe_allow_html=True)
