import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
# Fuentes de datos
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

# --- 2. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de borrado potenciado
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 3. FUNCIONES DE LIMPIEZA Y SEGURIDAD ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split('.')[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

# --- 4. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .card-cosecha { background: #e8f5e9 !important; border-left: 10px solid #2e7d32 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #1b5e20; }
    .route-txt { font-size: 22px; font-weight: 900; text-transform: uppercase; margin-bottom: 5px; }
    .btn-wsp { background-color: #2e7d32; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 15px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

st.markdown("<h1 style='text-align:center;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME COSECHA"])

# --- TAB 3: ARRIME COSECHA (VISTA SIMPLIFICADA) ---
with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 SECCIÓN ESPECIAL: ARRIME DE COSECHA</h3>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns([1, 2.2])
    
    with col_a1:
        with st.form("f_arr", clear_on_submit=True):
            z_loc = st.text_input("📍 Zona (Ej: Crispi)")
            g_det = st.text_input("🌾 Grano/Detalle (Ej: Soja)")
            t_val = st.text_input("💰 Tarifa (Ej: $13.500)")
            w_arr = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR ARRIME"):
                # Se guarda toda la info, pero se mostrará filtrada
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA", 
                    "entry.170847116": z_loc, 
                    "entry.576675281": f"ARRIME|{g_det}|{t_val}", 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w_arr
                })
                st.cache_data.clear()
                st.rerun()

    with col_a2:
        if not df_ca_raw.empty:
            df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            cols_arr = st.columns(2)
            for i, (idx, r) in enumerate(df_arrime.iterrows()):
                with cols_arr[i % 2]:
                    # Visualización ciega: Solo muestra la Zona y el contacto oculto
                    st.markdown(f"""
                    <div class="card-cosecha">
                        <div class="route-txt">📍 ARRIME {str(r[2]).upper()}</div>
                        <b>📱 TEL:</b> {ocultar_telefono(r[4])}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=Hola, consulto por el arrime en {r[2]}" 
                           target="_blank" class="btn-wsp">🚜 CONTACTAR AHORA</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.get('admin_mode', False):
                        if st.button(f"🗑️ BORRAR", key=f"del_{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r[0]}"})
                            st.cache_data.clear()
                            st.rerun()

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)
