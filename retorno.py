import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime
import math

# ============================================================
# 1. CONFIGURACIÓN Y BLINDAJE (IGNACIO DIAZ)
# ============================================================
CREADOR = "Ignacio Diaz"

# IDs de Google Sheets (Asegúrate que las GID coincidan con tus hojas actuales)
SHEET_ID        = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES    = "1392659349"
GID_CARGAS      = "1267917528"
GID_VIP         = "968995524"

# Configuración de tiempos y seguridad
HORAS_EXPIRACION = 72
WSP_SOPORTE      = "5493406649346"

# Coordenadas para cálculo de cercanía (Lógica de Retorno)
COORDS_CIUDADES = {
    "SAN JORGE (SF)": (-31.896, -61.859), "ROSARIO (SF)": (-32.946, -60.639),
    "SANTA FE (SF)": (-31.633, -60.700),  "RAFAELA (SF)": (-31.250, -61.486),
    "CORDOBA (CBA)": (-31.413, -64.181),  "BAHIA BLANCA (BA)": (-38.718, -62.266),
    "QUEQUEN (BA)": (-38.541, -58.713),   "ZARATE (BA)": (-34.096, -59.024),
}

# ============================================================
# 2. FUNCIONES DE LÓGICA Y MENSAJERÍA
# ============================================================
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    if not clean: return "549"
    if clean.startswith("0"): clean = clean[1:]
    if not clean.startswith("549"): clean = "549" + clean
    return clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    clean_num = limpiar_wsp(num)
    ahora = datetime.now().strftime("%H:%M")
    if es_chofer:
        msg = f"Hola! Te contacto por tu camión en *Retorno Match* ({ahora}hs).\n📍 *Origen:* {origen}\n🏁 *Destino:* {destino}\n¿Sigue disponible?"
    else:
        msg = f"Hola! Me interesa la carga en *Retorno Match* ({ahora}hs).\n📦 *Ruta:* {origen} ➔ {destino}\n¿Sigue disponible el viaje?"
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def calcular_distancia(c1, c2):
    if c1 not in COORDS_CIUDADES or c2 not in COORDS_CIUDADES: return 9999
    lat1, lon1 = COORDS_CIUDADES[c1]
    lat2, lon2 = COORDS_CIUDADES[c2]
    return math.sqrt((lat1-lat2)**2 + (lon1-lon2)**2) * 111

@st.cache_data(ttl=60)
def cargar_datos():
    t = int(time.time())
    url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
    url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
    url_v  = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
    
    df_ch = pd.read_csv(url_ch).fillna("-")
    df_ca = pd.read_csv(url_ca).fillna("-")
    try:
        df_v = pd.read_csv(url_v, header=None)
        vips = [str(x).strip().upper() for x in df_v[0].tolist()]
    except: vips = []
    return df_ch, df_ca, vips

# ============================================================
# 3. INTERFAZ STREAMLIT (MODO OSCURO)
# ============================================================
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚛", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; color: #adbac7; }}
    .card {{ background: #1c2128; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }}
    .vip-tag {{ color: #f1c40f; font-weight: bold; border: 1px solid #f1c40f; padding: 2px 5px; border-radius: 5px; font-size: 0.8rem; }}
    </style>
    <h1 style='text-align: center; color: #539bf5;'>🚛 RETORNO MATCH VIP</h1>
    <p style='text-align: center; color: #8b949e;'>Sistema de Logística Inteligente | Creado por {CREADOR}</p>
""", unsafe_allow_html=True)

df_ch, df_ca, LISTA_VIPS = cargar_datos()

# --- SECCIÓN DE ACCESO ---
with st.sidebar:
    st.header("🔑 Acceso Clientes")
    user_cuit = st.text_input("Ingresa tu CUIT para ver contactos").strip().upper()
    es_vip = user_cuit in LISTA_VIPS
    
    if user_cuit:
        if es_vip:
            st.success("Acceso VIP Concedido")
        else:
            st.warning("CUIT no registrado en lista VIP")
            st.markdown(f"[Solicitar Acceso](https://api.whatsapp.com/send?phone={WSP_SOPORTE}&text=Hola%20Ignacio,%20quiero%20habilitar%20mi%20CUIT:%20{user_cuit})")

# --- BUSCADOR Y FILTROS ---
col_f1, col_f2 = st.columns(2)
with col_f1:
    orig_f = st.selectbox("Origen:", ["TODOS"] + sorted(list(COORDS_CIUDADES.keys())))
with col_f2:
    dest_f = st.selectbox("Destino:", ["TODOS"] + sorted(list(COORDS_CIUDADES.keys())))

tab1, tab2 = st.tabs(["🚛 Choferes Disponibles", "📦 Cargas Pendientes"])

# --- TABLA DE CHOFERES ---
with tab1:
    for _, fila in df_ch.iterrows():
        # Filtrado simple
        if orig_f != "TODOS" and fila['ORIGEN'] != orig_f: continue
        
        with st.container():
            st.markdown(f"""
            <div class="card">
                <span class="vip-tag">DISPONIBLE</span>
                <h3 style="margin:0;">{fila['ORIGEN']} ➔ {fila['DESTINO']}</h3>
                <p style="color:#8b949e; margin:5px 0;">Camión: {fila['EQUIPO']} | Fecha: {fila['Timestamp']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if es_vip:
                link = generar_wsp_link(fila['TELEFONO'], fila['ORIGEN'], fila['DESTINO'])
                st.link_button(f"📲 Contactar Chofer ({fila['TELEFONO']})", link)
            else:
                st.info("🔒 Contacto bloqueado. Ingresa un CUIT VIP válido.")

# --- TABLA DE CARGAS ---
with tab2:
    for _, fila in df_ca.iterrows():
        if dest_f != "TODOS" and fila['DESTINO'] != dest_f: continue
        
        st.markdown(f"""
        <div class="card" style="border-left: 5px solid #2ecc71;">
            <h3 style="margin:0;">Carga: {fila['PRODUCTO']}</h3>
            <p style="margin:5px 0;">{fila['ORIGEN']} ➔ {fila['DESTINO']}</p>
            <p style="font-size:0.9rem; color:#8b949e;">Publicado: {fila['Timestamp']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if es_vip:
            link_c = generar_wsp_link(fila['CONTACTO'], fila['ORIGEN'], fila['DESTINO'], es_chofer=False)
            st.link_button("☎️ Tomar Carga", link_c)

st.divider()
st.caption(f"© 2026 {CREADOR} - Todos los derechos reservados.")
