import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CARGAS = "1267917528"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ADMIN_PIN = "1323" 

# --- AUTO-REFRESH NATIVO ---
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

if time.time() - st.session_state.last_refresh > 10:
    st.session_state.last_refresh = time.time()
    st.cache_data.clear()
    st.rerun()

# --- 2. CARGA DE DATOS ULTRA-SEGURA ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros():
    try:
        t = int(time.time())
        # Forzamos a que no haya cabeceras para manejar índices fijos
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        df = pd.read_csv(url, header=None).fillna("-")
        
        if df.empty:
            return pd.DataFrame()
            
        # Filtrado de borrados y limpieza de basura
        mask_borrado = df.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
        df = df[~mask_borrado]
        
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 3. FUNCIONES DE LIMPIEZA ---
def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if not clean or len(clean) < 7: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = limpiar_dato_numerico(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 4. INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🌾", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .radar-container { background: #e74c3c; color: white; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .card-cosecha { background: #ffffff !important; border-left: 8px solid #2e7d32 !important; color: #1b5e20; border-radius: 10px; padding: 15px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .btn-wsp { background-color: #2e7d32; color: white !important; padding: 10px; border-radius: 5px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: white; padding: 30px; font-size: 14px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🌾 OPERATIVO ARRIME COSECHA</h1>", unsafe_allow_html=True)

if 'anuncios' not in st.session_state: st.session_state.anuncios = "¡Bienvenido al sistema!"
st.markdown(f'<div class="radar-container"><marquee>{st.session_state.anuncios} -- Creado por Ignacio Diaz</marquee></div>', unsafe_allow_html=True)

df_raw = cargar_datos_seguros()

# --- 5. LÓGICA DE VISUALIZACIÓN BLINDADA ---
if not df_raw.empty:
    # Filtramos filas que tengan la palabra "ARRIME" en cualquier parte
    df_arrime = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
    
    col1, col2 = st.columns(2)
    
    for i, (idx, r) in enumerate(df_arrime.iterrows()):
        try:
            # USAMOS LÓGICA DE SEGURIDAD PARA ACCEDER A COLUMNAS
            # Si r tiene menos de 5 elementos, este bloque fallará y saltará al 'except'
            if len(r) >= 5:
                # Mapeo manual basado en la estructura de tu Google Form:
                # 0:MarcaTemporal, 1:Tipo, 2:Zona, 3:Detalle, 4:WhatsApp
                zona = str(r[2]).upper()
                detalle = str(r[3])
                telefono = str(r[4])
                
                texto_wsp = urllib.parse.quote(f"🌾 *OPERATIVO COSECHA*\nHola, me contacto por el arrime en {zona}.\nDetalle: {detalle}")
                
                with col1 if i % 2 == 0 else col2:
                    st.markdown(f'''
                        <div class="card-cosecha">
                            <div style="font-size: 18px; font-weight: bold; color: #1e3799;">📍 {zona}</div>
                            <div style="margin: 8px 0; color: #333;">{detalle}</div>
                            <div style="font-size: 12px; color: #666;">📞 {ocultar_telefono(telefono)}</div>
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(telefono)}&text={texto_wsp}" target="_blank" class="btn-wsp">🚜 CONTACTAR</a>
                        </div>
                    ''', unsafe_allow_html=True)
        except Exception:
            continue # Si una fila está rota, la salta y sigue con la siguiente

# --- 6. PIE DE PÁGINA ---
st.markdown(f"""
<div class="legal-footer">
    <hr style="border-color: rgba(255,255,255,0.1);">
    <p><b>Creado por Ignacio Diaz</b></p>
    <p>© 2026 RETORNO MATCH VIP - San Jorge, Santa Fe</p>
</div>
""", unsafe_allow_html=True)

# --- 7. PANEL DE CONTROL ---
with st.expander("⚙️"):
    pin = st.text_input("PIN:", type="password")
    if pin == ADMIN_PIN:
        st.write("Modo Administrador Activo")
        # Aquí puedes agregar el formulario de carga si lo necesitas de nuevo
