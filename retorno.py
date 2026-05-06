import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
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

# --- 2. MOTOR DE LIMPIEZA PROFESIONAL (SIN COMAS NI DECIMALES) ---
def limpiar_dato(dato):
    """Limpia CUITs, IDs y códigos: elimina .0 y comas de miles"""
    s = str(dato).replace(".0", "").replace(",", "").strip()
    return "".join(filter(str.isdigit, s))

def format_wsp(num):
    """Asegura formato de WhatsApp internacional sin errores"""
    clean = limpiar_dato(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_tel(num):
    clean = limpiar_dato(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 3. CARGA DE DATOS SEGUROS CON BLINDAJE ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Lógica de Borrado Ignacio Diaz
        if not df_ca.empty:
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask_borrado].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask_borrado]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [limpiar_dato(x) for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. INTERFAZ Y ESTILOS VIP (REDISEÑO NACHO) ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide", page_icon="⭐")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .glass-card {
        background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 20px; margin-bottom: 15px; transition: 0.3s;
    }
    .glass-card:hover { border-color: #f1c40f; transform: scale(1.005); }
    .vip-border { border-left: 8px solid #f1c40f !important; background: rgba(241, 196, 15, 0.05); }
    .route-header { font-size: 1.3rem; font-weight: 800; color: #f1c40f; text-transform: uppercase; }
    .btn-wsp {
        background: #238636; color: white !important; text-align: center;
        padding: 12px; border-radius: 8px; display: block;
        text-decoration: none; font-weight: bold; margin-top: 10px;
    }
    .btn-wsp:hover { background: #2ea043; }
    .footer { text-align: center; padding: 50px; border-top: 1px solid #30363d; margin-top: 60px; color: #8b949e; }
    .badge-new { background: #da3633; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; margin-right: 8px; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()
ahora = datetime.now()

# --- 5. LÓGICA DE FILTRADO Y MUESTRA ---
st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"<p style='color:#f1c40f;'>Estructura Nacho 360° | <b>Ignacio Diaz</b></p>", unsafe_allow_html=True)

# Filtros Inteligentes
c1, c2, c3 = st.columns(3)
with c1: f_o = st.text_input("📍 ORIGEN (Provincia o Ciudad):").upper()
with c2: f_d = st.text_input("🏁 DESTINO (Provincia o Ciudad):").upper()
with c3: f_q = st.text_input("🔍 PRODUCTO / EMPRESA:").upper()

tab1, tab2 = st.tabs(["🚀 CAMIONES DISPONIBLES", "📦 CARGAS DISPONIBLES"])

with tab1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if (f_o in str(r[1]).upper()) and (f_d in str(r[2]).upper()) and (f_q in str(r).upper()):
                cuit_limpio = limpiar_dato(r[4])
                es_vip = cuit_limpio in LISTA_VIPS
                st.markdown(f"""
                <div class="glass-card {'vip-border' if es_vip else ''}">
                    {f'<span style="color:#f1c40f; font-weight:bold;">⭐ MIEMBRO VIP</span>' if es_vip else ''}
                    <div class="route-header">{r[1]} ➔ {r[2]}</div>
                    <p style="margin:5px 0;">🚛 <b>EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit_limpio} | 📱 <b>TEL:</b> {ocultar_tel(r[5])}</p>
                    <a href="https://wa.me/{format_wsp(r[5])}" class="btn-wsp">CONTACTAR CHOFER</a>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            # Validación de tiempo para exclusividad
            try:
                ts = pd.to_datetime(r[0], dayfirst=True, errors='coerce')
                minutos = (ahora - ts).total_seconds() / 60
            except: minutos = 999
            
            if (f_o in str(r[1]).upper()) and (f_d in str(r[2]).upper()) and (f_q in str(r).upper()):
                if minutos < TIEMPO_EXCLUSIVO_MIN:
                    st.warning(f"🔒 CARGA RESERVADA VIP (Disponible para todos en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min)")
                else:
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 8px solid #3498db;">
                        <div class="route-header" style="color:#3498db;">{r[1]} ➔ {r[2]}</div>
                        <p style="margin:5px 0;">📦 <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]} | 📱 <b>TEL:</b> {ocultar_tel(r[4])}</p>
                        <a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp" style="background:#3498db;">POSTULARME A CARGA</a>
                    </div>
                    """, unsafe_allow_html=True)

# --- 6. PIE DE PÁGINA (SISTEMA PROTEGIDO) ---
st.markdown(f"""
<div class="footer">
    <h2 style="color:white;">CREADO POR IGNACIO DIAZ</h2>
    <p>SISTEMA DE LOGÍSTICA ESTRUCTURA NACHO | © 2026</p>
    <p style="font-size:0.8rem; opacity:0.5;">Queda prohibida la reproducción parcial o total del código sin consentimiento del autor.</p>
</div>
""", unsafe_allow_html=True)
