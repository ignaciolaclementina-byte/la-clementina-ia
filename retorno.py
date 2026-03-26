import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CARGAS = "1267917528"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ADMIN_PIN = "1323" 

# --- 2. CARGA DE DATOS ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        return df_ca
    except:
        return pd.DataFrame()

df_ca_raw = cargar_datos_seguros()

# --- 3. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num)))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 4. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP - COSECHA", page_icon="🌾", layout="wide")

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .btn-wsp { background-color: #2e7d32; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🌾 OPERATIVO ARRIME COSECHA</h1>", unsafe_allow_html=True)

# --- 5. PANEL ADMINISTRADOR ---
if st.session_state.admin_mode:
    col_a1, col_a2 = st.columns([1, 2])
    with col_a1:
        st.markdown("<h4 style='color:white;'>📢 Publicar Arrime</h4>", unsafe_allow_html=True)
        with st.form("f_arr", clear_on_submit=False):
            z_loc = st.text_input("📍 Zona")
            g_det = st.text_input("🌾 Detalle")
            t_val = st.text_input("💰 Tarifa")
            w_arr = st.text_input("📱 WhatsApp de contacto")
            
            if st.form_submit_button("✅ GUARDAR Y GENERAR TEXTO"):
                # Guardar en Google Sheets
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA", 
                    "entry.170847116": z_loc, 
                    "entry.576675281": f"ARRIME|{g_det}|{t_val}", 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w_arr
                })
                st.success("¡Datos guardados en la web!")
                
                # Generar texto para COPIAR Y PEGAR
                texto_para_canal = (
                    f"🌾 *NUEVO OPERATIVO DE ARRIME*\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"📍 *ZONA:* {z_loc}\n"
                    f"📝 *DETALLE:* {g_det}\n"
                    f"💰 *TARIFA:* {t_val}\n\n"
                    f"🚛 *ANOTARSE AQUÍ:* \n"
                    f"https://retorno-match-sanjorge.streamlit.app/\n\n"
                    f"✅ _Gestionado por Ignacio Diaz_"
                )
                
                st.markdown("---")
                st.markdown("📋 **COPIÁ ESTE TEXTO PARA TU CANAL:**")
                st.code(texto_para_canal, language="text") # Esto crea el botón de copiar automático
                st.cache_data.clear()

    main_col = col_a2
else:
    main_col = st.container()

# --- 6. VISTA CHOFERES ---
with main_col:
    if not df_ca_raw.empty:
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        cols = st.columns(2)
        for i, (idx, r) in enumerate(df_arrime.iterrows()):
            if len(r) < 5: continue
            with cols[i % 2]:
                st.markdown(f'''
                    <div class="card-cosecha">
                        <h3>📍 {r[2]}</h3>
                        <b>DETALLE:</b> {r[3]}<br>
                        <b>TEL:</b> {ocultar_telefono(r[4])}<br><br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">🚜 CONTACTAR</a>
                    </div>
                ''', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown("<br><hr><center style='color:white;'>Creado por Ignacio Diaz © 2026</center>", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
