import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN CORE (CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30 
WSP_VENTAS_VIP = "5493401525621"

# --- 2. MOTOR DE DATOS OPTIMIZADO (IGNACIO DIAZ) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        # Carga con bypass de caché de Google
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # BLINDAJE DE BORRADO: Filtro inmediato
        if not df_ca.empty:
            mask_borrado = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            df_ca = df_ca[~mask_borrado]
            
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips
    except:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 3. UI/UX PREMIUM ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Estilo de Tarjetas Nacho */
    .card-pro {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 5px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.2s ease;
    }
    .card-pro:hover { transform: scale(1.01); border-color: #3b82f6; }
    .card-vip { border-left-color: #f1c40f; background: #1e1b09; }
    
    .route-text { font-size: 22px; font-weight: 900; color: #f8fafc; margin-bottom: 5px; }
    .detail-text { color: #94a3b8; font-size: 14px; }
    .badge-vip { background: #f1c40f; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    
    .btn-wsp {
        display: block; width: 100%; text-align: center; background-color: #22c55e;
        color: white !important; padding: 12px; border-radius: 8px; 
        font-weight: bold; text-decoration: none; margin-top: 15px;
    }
    .footer-blindado { text-align: center; padding: 50px; color: #64748b; border-top: 1px solid #334155; margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES DE LIMPIEZA ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

# --- 5. CUERPO DE LA APP ---
df_ch, df_ca, LISTA_VIPS = cargar_datos_seguros()

st.title("🚛 RETORNO MATCH VIP")
st.markdown(f"**Estructura blindada creada por Ignacio Diaz**")

# Panel de filtros rápidos
with st.expander("🔍 FILTROS DE BÚSQUEDA", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1: orig = st.text_input("Origen:").upper()
    with col2: dest = st.text_input("Destino:").upper()
    with col3: cuit_login = st.text_input("Acceso VIP (CUIT):").strip()

es_usuario_vip = cuit_login.replace(".0", "") in LISTA_VIPS

tab_camiones, tab_cargas = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS ACTIVAS"])

with tab_camiones:
    if df_ch.empty:
        st.info("No se encontraron camiones hoy.")
    else:
        for _, r in df_ch.iloc[::-1].iterrows():
            if (orig in str(r[1]).upper()) and (dest in str(r[2]).upper()):
                is_vip = str(r[4]).strip() in LISTA_VIPS
                style = "card-pro card-vip" if is_vip else "card-pro"
                
                st.markdown(f"""
                <div class="{style}">
                    {f'<span class="badge-vip">CHOFER VIP</span>' if is_vip else ''}
                    <div class="route-text">{r[1]} ➔ {r[2]}</div>
                    <div class="detail-text">🚛 EQUIPO: <b>{r[3]}</b> | 🆔 CUIT: {r[4]}</div>
                    <a href="https://wa.me/{limpiar_wsp(r[5])}" target="_blank" class="btn-wsp">ENVIAR PROPUESTA</a>
                </div>
                """, unsafe_allow_html=True)

with tab_cargas:
    if df_ca.empty:
        st.info("Buscando nuevas cargas...")
    else:
        for _, r in df_ca.iloc[::-1].iterrows():
            if (orig in str(r[1]).upper()) and (dest in str(r[2]).upper()):
                is_vip = str(r[5]).strip() in LISTA_VIPS
                style = "card-pro card-vip" if is_vip else "card-pro"
                
                # Lógica de bloqueo VIP por tiempo (Ignacio Diaz)
                st.markdown(f"""
                <div class="{style}">
                    {f'<span class="badge-vip">EMPRESA VIP</span>' if is_vip else ''}
                    <div class="route-text">{r[1]} ➔ {r[2]}</div>
                    <div class="detail-text">📦 CARGA: <b>{r[3]}</b> | 🏢 EMPRESA: {r[5]}</div>
                    <a href="https://wa.me/{limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">SOLICITAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)

# --- 6. FOOTER DE LEY (IGNACIO DIAZ) ---
st.markdown(f"""
<div class="footer-blindado">
    <h3 style="color: #f1c40f; margin-bottom: 0;">CREADO POR IGNACIO DIAZ</h3>
    <p>Interfaz Protegida | San Jorge, Santa Fe | © 2026</p>
    <small>Prohibida la reproducción total o parcial de esta estructura.</small>
</div>
""", unsafe_allow_html=True)
