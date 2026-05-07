import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN CORE (ESTRUCTURA IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ADMIN_PIN = "1323" 

# --- 2. MOTOR DE DATOS (ANTIFALLOS) ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        df_ca = pd.read_csv(url_ca).fillna("-")
        
        # Filtro de borrado agresivo
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            df_ca = df_ca[~mask]
            
        url_v = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}"
        df_v = pd.read_csv(url_v, header=None)
        vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        
        return df_ca, vips
    except:
        return pd.DataFrame(), []

# --- 3. ESTILOS VISUALES (MODO DARK PROFESIONAL) ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f8fafc; }
    .card-arrime {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-left: 6px solid #22c55e;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .card-vip { border-left-color: #f1c40f !important; }
    .title-arrime { color: #22c55e; font-size: 20px; font-weight: 800; }
    .badge-vip { background: #f1c40f; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; float: right; }
    .btn-wsp {
        display: block; width: 100%; text-align: center; background-color: #15803d;
        color: white !important; padding: 10px; border-radius: 8px; 
        font-weight: bold; text-decoration: none; margin-top: 15px;
    }
    .footer { text-align: center; padding: 40px; color: #64748b; border-top: 1px solid #334155; margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES DE APOYO ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

# --- 5. INTERFAZ ---
st.title("🌾 SECCIÓN ARRIME COSECHA")
st.markdown("Creado por **Ignacio Diaz**")

df_ca, vips = cargar_datos_seguros()

col_form, col_lista = st.columns([1, 2])

with col_form:
    st.subheader("Publicar Nuevo Arrime")
    with st.form("form_arrime", clear_on_submit=True):
        zona = st.text_input("📍 Zona/Localidad")
        detalle = st.text_input("🌾 Detalle (Cereal/Tarifa)")
        wsp = st.text_input("📱 WhatsApp de contacto")
        if st.form_submit_button("PUBLICAR ARRIME"):
            if zona and wsp:
                # El truco: Enviamos 'ARRIME' como origen para que el filtro lo reconozca
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME", 
                    "entry.170847116": zona, 
                    "entry.576675281": detalle, 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": wsp
                })
                st.success("Publicado! Actualizando...")
                time.sleep(2)
                st.rerun()

with col_lista:
    if df_ca.empty:
        st.info("No hay publicaciones activas.")
    else:
        # Filtramos solo lo que sea ARRIME o COSECHA
        df_arrime = df_ca[df_ca.astype(str).apply(lambda x: x.str.contains('ARRIME|COSECHA', case=False)).any(axis=1)]
        
        for i, row in df_arrime.iloc[::-1].iterrows():
            # Acceso por posición para evitar el KeyError de columnas
            # row[1] = Zona, row[2] = Detalle, row[4] = WhatsApp
            try:
                l_zona = row.iloc[1]
                l_det = row.iloc[2]
                l_wsp = row.iloc[4]
                
                st.markdown(f"""
                <div class="card-arrime">
                    <span class="badge-vip">VERIFICADO</span>
                    <div class="title-arrime">📍 {l_zona}</div>
                    <div style="margin-top: 10px;">{l_det}</div>
                    <a href="https://wa.me/{limpiar_wsp(l_wsp)}" target="_blank" class="btn-wsp">🚜 CONTACTAR AHORA</a>
                </div>
                """, unsafe_allow_html=True)
            except:
                continue

st.markdown("""
<div class="footer">
    <p>ESTRUCTURA PROTEGIDA - CREADO POR IGNACIO DIAZ</p>
    <p>© 2026 San Jorge, Santa Fe</p>
</div>
""", unsafe_allow_html=True)
