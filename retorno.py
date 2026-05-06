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

# --- 2. MOTOR DE DATOS (NÚCLEO NACHO) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Filtro de Borrado Avanzado
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

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 3. FUNCIONES DE LIMPIEZA (REQUERIMIENTO CÓDIGOS SIN COMAS) ---
def limpiar_dato(dato):
    s = str(dato).strip().replace(".0", "")
    return "".join(filter(str.isdigit, s))

def format_wsp(num):
    clean = limpiar_dato(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

# --- 4. INTERFAZ PROFESIONAL (ESTILOS BLACK & GOLD) ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: rgba(255,255,255,0.03);
        border-radius: 15px;
        padding: 20px;
        border-left: 5px solid #f1c40f;
        margin-bottom: 15px;
    }
    .vip-card {
        background: linear-gradient(145deg, #1a1a1a, #000000);
        border: 1px solid #f1c40f;
        box-shadow: 0 4px 15px rgba(241, 196, 15, 0.2);
    }
    .btn-wsp {
        background: #25D366;
        color: white !important;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        display: block;
        text-decoration: none;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. ENCABEZADO Y FILTROS ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"<p style='color:#f1c40f;'>Infraestructura de Datos: <b>{SHEET_ID}</b> | Creado por Ignacio Diaz</p>", unsafe_allow_html=True)

ahora = datetime.now()
c1, c2, c3 = st.columns(3)
with c1: b_o = st.selectbox("ORIGEN:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
with c2: b_d = st.selectbox("DESTINO:", ["CUALQUIERA"] + list(COORDS_PROV.keys()))
with c3: search = st.text_input("BÚSQUEDA RÁPIDA:").upper()

# --- 6. TABS OPERATIVAS ---
tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "📦 CARGAS", "🌾 COSECHA"])

with tab1:
    col_form, col_list = st.columns([1, 2])
    with col_form:
        st.subheader("Publicar Carga")
        with st.form("f1"):
            fo = st.selectbox("Prov. Origen", list(COORDS_PROV.keys()))
            fd = st.selectbox("Prov. Destino", list(COORDS_PROV.keys()))
            fw = st.text_input("WhatsApp de contacto")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": fo, "entry.170847116": fd, "entry.466540450": fw})
                st.success("Carga publicada")

    with col_list:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iterrows():
                # Lógica de filtrado
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and \
                   (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and \
                   (search in str(r).upper()):
                    
                    st.markdown(f"""
                    <div class="card">
                        <h3>{r[1]} ➔ {r[2]}</h3>
                        <p>🚛 <b>EQUIPO:</b> {r[3]} | 🆔 <b>ID:</b> {limpiar_dato(r[4])}</p>
                        <a href="https://wa.me/{format_wsp(r[5])}" class="btn-wsp">CONTACTAR CHOFER</a>
                    </div>
                    """, unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            st.markdown(f"""
            <div class="card vip-card">
                <span style="color:#f1c40f">⭐ CARGA VIP</span>
                <h3>{r[1]} ➔ {r[2]}</h3>
                <p>📦 <b>MERCADERÍA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}</p>
                <a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp">GESTIONAR CARGA</a>
            </div>
            """, unsafe_allow_html=True)

# --- 7. FOOTER BLINDADO ---
st.markdown(f"""
<div style="text-align:center; margin-top:50px; padding:30px; border-top:1px solid #333;">
    <h2 style="color:#f1c40f;">CREADO POR IGNACIO DIAZ Y SUS LEGALES</h2>
    <p>© 2026 RETORNO MATCH VIP - San Jorge, Santa Fe</p>
</div>
""", unsafe_allow_html=True)
