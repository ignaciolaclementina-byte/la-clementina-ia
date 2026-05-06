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

# --- 2. MOTOR DE LIMPIEZA DE DATOS (REQUERIMIENTO: SIN COMAS NI DECIMALES) ---
def limpiar_dato_numerico(dato):
    """Elimina .0 y comas de CUITs, IDs y teléfonos para vista limpia"""
    if pd.isna(dato) or dato == "-": return ""
    s = str(dato).split('.')[0].replace(',', '').replace(' ', '').strip()
    return "".join(filter(str.isdigit, s))

def format_wsp(num):
    """Formatea número para link de WhatsApp profesional"""
    clean = limpiar_dato_numerico(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = limpiar_dato_numerico(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 3. CARGA DE DATOS SEGUROS (FILTRO BORRADO IGNACIO DIAZ) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Blindaje de Borrado: Filtra filas con 'BORRADO'
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [limpiar_dato_numerico(x) for x in df_v[0].dropna().tolist()]
        
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. INTERFAZ Y ESTILOS (MANTIENE INTERFAZ ORIGINAL) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .card-white { background: white !important; border-left: 10px solid #3498db; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #1b5e20; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

df_ch_raw, df_ca_raw, LISTA_VIPS = cargar_datos_seguros()

# --- 5. LOGICA DE VISTA ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Filtros
c1, c2, c3 = st.columns(3)
with c1: b_o = st.text_input("📍 ORIGEN:").upper()
with c2: b_d = st.text_input("🏁 DESTINO:").upper()
with c3: b_q = st.text_input("🔎 BÚSQUEDA LIBRE:").upper()

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA"])

with tab1:
    if not df_ch_raw.empty:
        for _, r in df_ch_raw.iterrows():
            if (b_o in str(r[1]).upper()) and (b_d in str(r[2]).upper()) and (b_q in str(r).upper()):
                cuit = limpiar_dato_numerico(r[4])
                tel = format_wsp(r[5])
                es_vip = cuit in LISTA_VIPS
                st.markdown(f"""
                <div class="{'card-vip' if es_vip else 'card-white'}">
                    <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                    <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit} | 📱 <b>TEL:</b> {ocultar_telefono(r[5])}
                    <a href="https://wa.me/{tel}?text=Hola, te consulto por tu unidad en {r[1]}" class="btn-wsp">CONTACTAR CHOFER</a>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        for _, r in df_ca_raw.iterrows():
            if (b_o in str(r[1]).upper()) and (b_d in str(r[2]).upper()) and (b_q in str(r).upper()):
                tel_ca = format_wsp(r[4])
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #e74c3c;">
                    <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                    <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}
                    <a href="https://wa.me/{tel_ca}?text=Hola, me interesa la carga de {r[1]} a {r[2]}" class="btn-wsp" style="background:#e74c3c;">POSTULARME</a>
                </div>
                """, unsafe_allow_html=True)

with tab3:
    st.info("Sección de Arrime y Cosecha")
    # Lógica simplificada de arrime manteniendo tu estilo
    df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
    for _, r in df_arrime.iterrows():
        st.markdown(f'<div class="card-cosecha">📍 {r[2]}<br>{r[3]}<br><a href="https://wa.me/{format_wsp(r[4])}" class="btn-wsp" style="background:#2e7d32;">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)

# --- 6. PIE DE PÁGINA (BLINDADO) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 22px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP | San Jorge</p>
    <p>Estructura e Interfaz Blindada - Sistema de Gestión Logística</p>
</div>
""", unsafe_allow_html=True)
