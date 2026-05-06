import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime
import pytz

# --- IDENTIDAD Y ESTRUCTURA (IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# Configuración de página con estilo oscuro nativo
st.set_page_config(page_title="Retorno Match VIP", page_icon="🚛", layout="wide")

# --- UI/UX CUSTOM: ESTILO IGNACIO DIAZ ---
st.markdown("""
<style>
    /* Estética Dark Mode Enterprise */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Contenedor de Carga/Camión */
    .card-container {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        border-left: 6px solid #f1c40f; /* Amarillo Tráfico */
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .card-container:hover {
        transform: translateY(-2px);
        border-color: #f1c40f;
    }
    
    /* Etiquetas de estado */
    .tag-dispo { background: #f1c40f; color: #000; padding: 3px 10px; border-radius: 5px; font-weight: 800; font-size: 11px; }
    .tag-time { color: #8b949e; font-size: 11px; float: right; font-weight: bold; }
    
    /* Tipografía de Ruta */
    .ruta-header { font-size: 24px; font-weight: 900; color: #f0f6fc; margin: 10px 0; letter-spacing: -0.5px; }
    .info-line { font-size: 15px; color: #8b949e; margin-bottom: 6px; }
    .highlight { color: #f1c40f; font-weight: bold; }
    
    /* Botón WhatsApp Profesional */
    .btn-wsp {
        display: block; width: 100%; text-align: center; background-color: transparent;
        color: #ffffff !important; border: 1px solid #30363d; padding: 12px;
        border-radius: 8px; font-weight: 600; text-decoration: none; margin-top: 15px;
        transition: all 0.3s;
    }
    .btn-wsp:hover { background-color: #238636; border-color: #2ea043; }
    
    /* Footer Blindado */
    .footer-blindado {
        text-align: center; padding: 40px; border-top: 1px solid #30363d;
        margin-top: 50px; color: #8b949e;
    }
    .author-name { color: #f1c40f; font-weight: 900; letter-spacing: 2px; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DATOS (ANTI-ERROR N/A) ---
@st.cache_data(ttl=15)
def cargar_datos_maestros():
    try:
        t = int(time.time())
        # Cargamos usando índices de posición para que no importe si cambian los nombres de columnas
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        return df_ca, df_ch
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def limpiar_contacto(numero):
    """Limpia el número para que el link de WhatsApp nunca falle"""
    limpio = "".join(filter(str.isdigit, str(numero).split('.')[0]))
    if not limpio: return ""
    return "549" + limpio[-10:] if not limpio.startswith("549") else limpio

def hace_cuanto(timestamp):
    """Calcula el tiempo real de publicación (GMT-3)"""
    try:
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        dt = datetime.strptime(str(timestamp), "%d/%m/%Y %H:%M:%S").replace(tzinfo=tz)
        dif = datetime.now(tz) - dt
        minutos = int(dif.total_seconds() / 60)
        if minutos < 60: return f"Hace {minutos}m"
        return f"Hace {int(minutos/60)}h"
    except:
        return "Reciente"

# --- ESTRUCTURA DE LA APP ---
st.markdown("<h1>🚛 RETORNO MATCH <span style='color:#f1c40f'>VIP</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size:18px; margin-top:-15px; color:#8b949e;'>Gestión Logística Profesional | <b>San Jorge</b></p>", unsafe_allow_html=True)

df_cargas, df_choferes = cargar_datos_maestros()

# Panel de Filtros Superior
with st.expander("🔍 FILTRAR CARGAS Y CAMIONES", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        f_origen = st.text_input("📍 Punto de Origen", "").upper()
    with col2:
        f_equipo = st.multiselect("🚛 Tipo de Equipo", ["Sider", "Batea", "Chasis", "Acoplado", "Semi", "Térmico"])

# Tabs de navegación
tab_cargas, tab_camiones = st.tabs(["📦 CARGAS DISPONIBLES", "🚚 CAMIONES EN RADAR"])

with tab_cargas:
    if df_cargas.empty:
        st.info("Buscando nuevas cargas en el servidor...")
    else:
        # Invertimos el DF para mostrar lo más reciente arriba
        for _, row in df_cargas.iloc[::-1].iterrows():
            if len(row) < 5: continue
            
            # Datos por posición (0:Timestamp, 1:Origen, 2:Destino, 3:Mercaderia, 4:Wsp, 5:Empresa)
            ts, orig, dest, merc, wsp_raw = row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4]
            empr = row.iloc[5] if len(row) > 5 else "Directo"
            
            if f_origen and f_origen not in str(orig).upper(): continue
            
            wsp = limpiar_contacto(wsp_raw)
            tiempo = hace_cuanto(ts)
            msg = urllib.parse.quote(f"Hola {empr}, vi tu carga en Retorno Match VIP. Me interesa el viaje de {orig} a {dest} ({merc}).")

            st.markdown(f"""
            <div class="card-container">
                <span class="tag-dispo">DISPONIBLE</span>
                <span class="tag-time">🕒 {tiempo}</span>
                <div class="ruta-header">{orig} ➔ {dest}</div>
                <div class="info-line">📦 <b>Carga:</b> <span class="highlight">{merc}</span></div>
                <div class="info-line">🏢 <b>Empresa:</b> {empr}</div>
                <a href="https://wa.me/{wsp}?text={msg}" target="_blank" class="btn-wsp">📲 CONTACTAR AHORA</a>
            </div>
            """, unsafe_allow_html=True)

with tab_camiones:
    if df_choferes.empty:
        st.info("Sincronizando radar de choferes...")
    else:
        for _, row in df_choferes.iloc[::-1].iterrows():
            if len(row) < 5: continue
            
            # Datos (0:Timestamp, 1:Origen, 2:Destino, 3:Equipo, 4:ID/CUIT, 5:Wsp)
            ts, orig, dest, equi, cuit = row.iloc[0], row.iloc[1], row.iloc[2], row.iloc[3], row.iloc[4]
            wsp_raw = row.iloc[5] if len(row) > 5 else cuit
            
            if f_origen and f_origen not in str(orig).upper(): continue
            if f_equipo and str(equi).title() not in f_equipo: continue
            
            wsp = limpiar_contacto(wsp_raw)
            tiempo = hace_cuanto(ts)
            msg = urllib.parse.quote(f"Hola, te contacto por tu unidad {equi} en Retorno Match VIP. ¿Sigue disponible en {orig}?")

            st.markdown(f"""
            <div class="card-container" style="border-left-color: #3498db;">
                <span class="tag-dispo" style="background:#3498db; color:white;">CAMIÓN LIBRE</span>
                <span class="tag-time">🕒 {tiempo}</span>
                <div class="ruta-header">{orig} ➔ {dest}</div>
                <div class="info-line">🚛 <b>Unidad:</b> <span class="highlight">{equi}</span></div>
                <div class="info-line">🆔 <b>ID/CUIT:</b> {cuit}</div>
                <a href="https://wa.me/{wsp}?text={msg}" target="_blank" class="btn-wsp" style="border-color:#3498db;">📩 OFRECER CARGA</a>
            </div>
            """, unsafe_allow_html=True)

# Botón de Actualización Manual
if st.button("🔄 ACTUALIZAR TODA LA BASE DE DATOS", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- FOOTER LEGAL E IDENTIDAD (IGNACIO DIAZ) ---
st.markdown(f"""
<div class="footer-blindado">
    <p style="margin-bottom:5px;">Estructura de Interfaz Blindada v2.6</p>
    <p class="author-name">CREADO POR IGNACIO DIAZ</p>
    <p style="font-size:11px; opacity:0.6;">© 2026 Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
