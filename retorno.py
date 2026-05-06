import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
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

# --- 2. FUNCIONES DE LÓGICA Y DATOS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Blindaje de Borrado
        if not df_ca.empty:
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask_borrado].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            r = 6371 
            dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return f"📍 {int(r * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))} km"
        return ""
    except: return ""

# --- 3. INTERFAZ Y ESTILOS (SISTEMA PREMIUM) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Cards Mejoradas */
    .vip-card {
        background: linear-gradient(145deg, #1e1e1e, #252525);
        border: 1px solid #f1c40f;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(241, 196, 15, 0.1);
    }
    .normal-card {
        background: #161b22;
        border-left: 5px solid #3498db;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
    }
    .dist-badge { color: #f1c40f; font-weight: bold; font-size: 0.9em; }
    .btn-wsp {
        background-color: #25D366;
        color: white !important;
        padding: 8px 15px;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        font-weight: bold;
        margin-top: 10px;
    }
    .radar-container {
        background: #1f1f1f;
        border: 1px solid #333;
        color: #00ff00;
        font-family: 'Courier New', Courier, monospace;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. EJECUCIÓN ---
df_ch, df_ca, vips = cargar_datos_seguros()
ahora = datetime.now()

st.title("🚛 RETORNO MATCH VIP")
st.caption("Estructura Blindada | Creado por Ignacio Diaz")

# Radar de anuncios
radar_txt = f"SISTEMA ACTIVO -- BIENVENIDO IGNACIO DIAZ -- ACTUALIZADO: {ahora.strftime('%H:%M:%S')}"
st.markdown(f'<div class="radar-container"><marquee scrollamount="5">{radar_txt}</marquee></div>', unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

with t1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Publicar Carga")
        with st.form("cargas_form"):
            # Campos simplificados para mayor velocidad
            origen = st.text_input("Origen (Provincia/Localidad)")
            destino = st.text_input("Destino (Provincia/Localidad)")
            wsp = st.text_input("WhatsApp de contacto")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": origen, "entry.170847116": destino, "entry.466540450": wsp})
                st.success("Carga subida.")
                st.rerun()

    with col2:
        if not df_ch.empty:
            for _, r in df_ch.tail(10).iterrows():
                dist = calcular_distancia(r[1], r[2])
                st.markdown(f"""
                <div class="normal-card">
                    <span class="dist-badge">{dist}</span>
                    <div style="font-size: 1.2em; font-weight: bold; color: #3498db;">{r[1]} ➔ {r[2]}</div>
                    <small>Equipo: {r[3]}</small><br>
                    <a href="https://wa.me/{limpiar_wsp(r[5])}" class="btn-wsp">Contactar Chofer</a>
                </div>
                """, unsafe_allow_html=True)

# Footer Legal Blindado
st.markdown("---")
st.markdown(f"""
    <div style="text-align: center; opacity: 0.6; padding: 20px;">
        <p>Creado por <b>Ignacio Diaz</b></p>
        <p>© 2026 Todos los derechos reservados.</p>
    </div>
""", unsafe_allow_html=True)
