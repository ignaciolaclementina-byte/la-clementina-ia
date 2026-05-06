import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime

# --- CONFIGURACIÓN BLINDADA (CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

st.set_page_config(page_title="Retorno Match VIP", page_icon="🚛", layout="wide", initial_sidebar_state="collapsed")

# --- CSS PREMIUM (UI/UX) ---
st.markdown("""
<style>
    /* Fondo oscuro moderno */
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    
    /* Tarjetas de Logística */
    .log-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .log-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(241, 196, 15, 0.15);
        border-color: #f1c40f;
    }
    
    /* Tipografía y Badges */
    .route-title { font-size: 22px; font-weight: 800; color: #f8fafc; margin-bottom: 5px; }
    .badge-vip { background-color: #f1c40f; color: #000; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 900; letter-spacing: 0.5px; }
    .badge-time { background-color: #ef4444; color: #fff; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
    .detail-text { font-size: 15px; color: #94a3b8; margin: 5px 0; }
    
    /* Botones */
    .btn-wsp {
        display: inline-block; width: 100%; text-align: center; background-color: #25D366; color: white !important; 
        padding: 12px; border-radius: 8px; font-weight: bold; text-decoration: none; margin-top: 15px;
        transition: background-color 0.3s;
    }
    .btn-wsp:hover { background-color: #128C7E; }
    
    /* Footer */
    .footer-auth { text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid #334155; color: #64748b; font-size: 14px; }
    
    /* Métricas */
    div[data-testid="metric-container"] { background-color: #1e293b; border-radius: 10px; padding: 15px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# --- MOTOR DE DATOS ROBUSTO ---
@st.cache_data(ttl=15) # Actualización ultra rápida
def fetch_data():
    try:
        t = int(time.time())
        # Cargas
        url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        df_ca = pd.read_csv(url_ca)
        
        # Choferes
        url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
        df_ch = pd.read_csv(url_ch)
        return df_ca, df_ch
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

def limpiar_numero(num_str):
    """Elimina comas, decimales y caracteres raros de CUITs y Teléfonos"""
    limpio = str(num_str).split('.')[0].replace(',', '').replace(' ', '').replace('-', '')
    return "".join(filter(str.isdigit, limpio))

# --- INTERFAZ ---
st.markdown("<h1>🚛 RETORNO MATCH <span style='color:#f1c40f;'>VIP</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#94a3b8; font-size:18px;'>Gestión Logística Profesional y Cargas de Retorno</p>", unsafe_allow_html=True)

df_cargas, df_choferes = fetch_data()

# --- DASHBOARD METRICAS ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Cargas Activas", len(df_cargas) if not df_cargas.empty else 0, "Hoy")
col_m2.metric("Camiones Disponibles", len(df_choferes) if not df_choferes.empty else 0, "Hoy")
col_m3.metric("Estado del Sistema", "ONLINE", "Conectado")

st.markdown("---")

# --- PANEL DE CONTROL Y BUSQUEDA ---
with st.expander("🔍 FILTROS DE BÚSQUEDA AVANZADA", expanded=True):
    col_f1, col_f2, col_f3 = st.columns(3)
    filtro_origen = col_f1.text_input("📍 Origen (Ej: Santa Fe)").upper()
    filtro_destino = col_f2.text_input("🏁 Destino (Ej: Cordoba)").upper()
    filtro_libre = col_f3.text_input("📦 Palabra Clave (Ej: Soja, Sider)").upper()

# --- TABS PRINCIPALES ---
tab1, tab2 = st.tabs(["🏢 CARGAS DISPONIBLES", "🚀 CAMIONES DISPONIBLES"])

with tab1:
    if df_cargas.empty:
        st.info("No hay cargas disponibles en este momento o verificando conexión...")
    else:
        for idx in range(len(df_cargas) - 1, -1, -1): # Recorrer al revés (más recientes primero)
            row = df_cargas.iloc[idx]
            if len(row) < 5: continue
            
            # Mapeo seguro por índice (ignora los nombres de columnas de Google Forms)
            fecha_str = str(row.iloc[0])
            origen = str(row.iloc[1]).upper()
            destino = str(row.iloc[2]).upper()
            mercaderia = str(row.iloc[3]).title()
            wsp_raw = str(row.iloc[4])
            empresa = str(row.iloc[5]).title() if len(row) > 5 else "Empresa Verificada"
            
            # Aplicar filtros
            if filtro_origen and filtro_origen not in origen: continue
            if filtro_destino and filtro_destino not in destino: continue
            if filtro_libre and filtro_libre not in mercaderia.upper() and filtro_libre not in empresa.upper(): continue

            wsp_clean = limpiar_numero(wsp_raw)
            if not wsp_clean.startswith("549"): wsp_clean = "549" + wsp_clean[-10:] # Forzar formato Arg

            msg_profesional = urllib.parse.quote(f"Hola {empresa}. Me comunico desde Retorno Match VIP. Estoy interesado en la carga de {mercaderia} con origen en {origen} y destino {destino}. ¿Sigue disponible?")
            link_wsp = f"https://wa.me/{wsp_clean}?text={msg_profesional}"

            st.markdown(f"""
            <div class="log-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span class="badge-vip">⭐ CARGA VIP</span>
                    <span class="badge-time">ACTIVA</span>
                </div>
                <div class="route-title">{origen} ➔ {destino}</div>
                <div class="detail-text">📦 <b>Mercadería:</b> {mercaderia}</div>
                <div class="detail-text">🏢 <b>Empresa:</b> {empresa}</div>
                <a href="{link_wsp}" target="_blank" class="btn-wsp">📲 CONTACTAR POR WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    if df_choferes.empty:
        st.info("No hay camiones disponibles en este momento...")
    else:
        for idx in range(len(df_choferes) - 1, -1, -1):
            row = df_choferes.iloc[idx]
            if len(row) < 5: continue
            
            # Mapeo Choferes
            fecha_str = str(row.iloc[0])
            origen_ch = str(row.iloc[1]).upper()
            destino_ch = str(row.iloc[2]).upper()
            equipo = str(row.iloc[3]).title()
            cuit_raw = str(row.iloc[4])
            wsp_raw = str(row.iloc[5]) if len(row) > 5 else cuit_raw # A veces el user invierte CUIT y WSP

            cuit_clean = limpiar_numero(cuit_raw)
            wsp_clean = limpiar_numero(wsp_raw)
            
            if len(wsp_clean) < 10: wsp_clean = cuit_clean # Fallback si se invirtieron en el form
            if not wsp_clean.startswith("549"): wsp_clean = "549" + wsp_clean[-10:]

            msg_ch = urllib.parse.quote(f"Hola. Te contacto por tu unidad ({equipo}) publicada en Retorno Match VIP desde {origen_ch} hacia {destino_ch}. Tengo un viaje para ofrecerte.")
            link_wsp_ch = f"https://wa.me/{wsp_clean}?text={msg_ch}"

            st.markdown(f"""
            <div class="log-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <span style="background-color:#3b82f6; color:white; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold;">🚛 CAMIÓN DISPONIBLE</span>
                </div>
                <div class="route-title">{origen_ch} ➔ {destino_ch}</div>
                <div class="detail-text">⚙️ <b>Equipo:</b> {equipo}</div>
                <div class="detail-text">🆔 <b>CUIT/ID:</b> {cuit_clean}</div>
                <a href="{link_wsp_ch}" target="_blank" class="btn-wsp" style="background-color:#3b82f6;">📲 OFRECER VIAJE</a>
            </div>
            """, unsafe_allow_html=True)

# --- REFRESH MANUAL ---
if st.button("🔄 Sincronizar Base de Datos Ahora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# --- FOOTER BLINDADO ---
st.markdown("""
<div class="footer-auth">
    <h3 style="color:#f8fafc; margin-bottom:5px;">Estructura Blindada v2.0</h3>
    <p>Diseño y Desarrollo de Software Exclusivo</p>
    <p style="color:#f1c40f; font-weight:bold; letter-spacing: 1px;">CREADO POR IGNACIO DIAZ</p>
    <p style="font-size:12px; opacity:0.5;">© 2026 Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
