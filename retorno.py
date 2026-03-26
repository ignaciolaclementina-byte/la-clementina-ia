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

# --- MEJORA: AUTO-ACTUALIZACIÓN NATIVA (Cada 30 seg) ---
# Esto reemplaza la librería que tiraba error y mantiene la estructura
if "refresh_count" not in st.session_state:
    st.session_state.refresh_count = 0

# Fragmento que se ejecuta solo para recargar datos sin afectar el formulario
@st.fragment(run_every="30s")
def fragmento_actualizacion():
    st.session_state.refresh_count += 1

fragmento_actualizacion()

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros(count):
    try:
        t = int(time.time())
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        return df_ca
    except:
        return pd.DataFrame()

# Pasamos el refresh_count para forzar la recarga de la cache
df_ca_raw = cargar_datos_seguros(st.session_state.refresh_count)

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = limpiar_dato_numerico(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 5. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP - COSECHA", page_icon="🌾", layout="wide")

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'anuncios' not in st.session_state: st.session_state.anuncios = "¡Bienvenido al Operativo Cosecha!"

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 20px; margin-bottom: 15px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #2e7d32; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-difusion { background-color: #25D366; color: white !important; padding: 15px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 15px; border: 2px solid white; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🌾 OPERATIVO ARRIME COSECHA</h1>", unsafe_allow_html=True)

radar_txt = f"{st.session_state.anuncios} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

# --- 6. SECCIÓN DE PUBLICACIÓN (SÓLO ADMINISTRADOR) ---
if st.session_state.admin_mode:
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        st.markdown("<h4 style='color:white;'>📢 Cargar Nuevo Arrime</h4>", unsafe_allow_html=True)
        with st.form("f_arr", clear_on_submit=False):
            z_loc = st.text_input("📍 Zona")
            g_det = st.text_input("🌾 Detalle")
            t_val = st.text_input("💰 Tarifa")
            w_arr = st.text_input("📱 WhatsApp de contacto")
            
            submit = st.form_submit_button("✅ PUBLICAR Y DIFUNDIR")
            
            if submit:
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA", 
                    "entry.170847116": z_loc, 
                    "entry.576675281": f"ARRIME|{g_det}|{t_val}", 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w_arr
                })
                st.success("¡Guardado!")
                mensaje_canal = f"🌾 *NUEVO ARRIME*\n📍 ZONA: {z_loc}\n📝 DETALLE: {g_det}\n💰 TARIFA: {t_val}\n🚛 POSTULATE: https://retorno-match-sanjorge.streamlit.app/\n✅ _Ignacio Diaz_"
                st.code(mensaje_canal, language="text")
                st.cache_data.clear()
    main_col = col_a2
else:
    main_col = st.container()

# --- 7. VISUALIZACIÓN DE CARDS ---
with main_col:
    if not df_ca_raw.empty:
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        cols_arr = st.columns(2)
        for i, (idx, r) in enumerate(df_arrime.iterrows()):
            if len(r) < 5: continue
            with cols_arr[i % 2]:
                st.markdown(f'''
                    <div class="card-cosecha">
                        <div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>
                        <b>DETALLE:</b> {r[3]}<br>
                        <b>TEL:</b> {ocultar_telefono(r[4])}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">🚜 CONTACTAR</a>
                    </div>
                ''', unsafe_allow_html=True)
                if st.session_state.admin_mode:
                    if st.button(f"🗑️ BORRAR #{i}", key=f"del_{idx}"):
                        requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r[0]}"})
                        st.cache_data.clear(); st.rerun()

# --- 8. PIE DE PÁGINA (AUTORÍA) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ACCESO"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
