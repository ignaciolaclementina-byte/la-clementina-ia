import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime
import pytz

# --- CONFIGURACIÓN Y BLINDAJE ---
# Creado por Ignacio Diaz
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

st.set_page_config(page_title="Retorno Match VIP", page_icon="🚛", layout="wide")

# --- ESTILOS CSS PROFESIONALES (BASADO EN LA INTERFAZ ORIGINAL) ---
st.markdown("""
<style>
    /* Fondo principal y tipografía */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Estructura de la tarjeta principal */
    .match-card {
        background-color: #1a1e24;
        border-radius: 8px;
        border-left: 5px solid #f1c40f;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    .match-card:hover { transform: translateY(-2px); border-left: 5px solid #e6b800; }
    
    /* Etiquetas y textos */
    .badge-disponible {
        background-color: #f1c40f; color: #000000; font-weight: 800; font-size: 11px;
        padding: 4px 10px; border-radius: 4px; display: inline-block; margin-bottom: 12px;
    }
    .badge-tiempo {
        background-color: #2d3748; color: #a0aec0; font-size: 11px;
        padding: 4px 8px; border-radius: 4px; float: right; font-weight: bold;
    }
    .ruta-texto { font-size: 24px; font-weight: 800; color: #ffffff; margin-bottom: 15px; letter-spacing: 0.5px; }
    .info-texto { font-size: 15px; color: #cbd5e0; margin-bottom: 8px; display: flex; align-items: center; }
    .info-icon { width: 20px; text-align: center; margin-right: 10px; display: inline-block; }
    
    /* Botón WhatsApp */
    .btn-whatsapp {
        display: block; width: 100%; background-color: transparent; color: #ffffff !important;
        text-align: center; padding: 12px; border: 1px solid #374151; border-radius: 6px;
        text-decoration: none; font-weight: 600; margin-top: 20px; transition: all 0.3s ease;
    }
    .btn-whatsapp:hover { background-color: #25D366; border-color: #25D366; color: #ffffff !important; }
    
    /* Footer */
    .footer-legal {
        text-align: center; margin-top: 60px; padding-top: 20px; border-top: 1px solid #2d3748;
        color: #718096; font-size: 13px; font-weight: 500;
    }
    .creator-name { color: #f1c40f; font-weight: 800; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE PROCESAMIENTO ---
@st.cache_data(ttl=30)
def cargar_datos():
    """Lee los datos directamente ignorando nombres de columnas para evitar el error N/A"""
    try:
        url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}"
        url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}"
        df_ca = pd.read_csv(url_ca).fillna("")
        df_ch = pd.read_csv(url_ch).fillna("")
        return df_ca, df_ch
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def limpiar_telefono(num_str):
    """Limpia caracteres y asegura el formato internacional para Argentina"""
    limpio = str(num_str).split('.')[0].replace(',', '').replace(' ', '').replace('-', '').replace('+', '')
    limpio = "".join(filter(str.isdigit, limpio))
    if not limpio: return ""
    if limpio.startswith("15") and len(limpio) == 10: limpio = limpio[2:]
    if not limpio.startswith("549"): limpio = "549" + limpio[-10:]
    return limpio

def calcular_tiempo_transcurrido(fecha_str):
    """Calcula hace cuánto se publicó el registro"""
    try:
        tz = pytz.timezone('America/Argentina/Buenos_Aires')
        # Asumiendo formato DD/MM/YYYY HH:MM:SS de Google Forms
        fecha_obj = datetime.strptime(str(fecha_str), "%d/%m/%Y %H:%M:%S")
        fecha_obj = tz.localize(fecha_obj)
        ahora = datetime.now(tz)
        diff = ahora - fecha_obj
        
        minutos = int(diff.total_seconds() / 60)
        if minutos < 60: return f"Hace {minutos} min"
        horas = int(minutos / 60)
        if horas < 24: return f"Hace {horas} hs"
        return f"Hace {int(horas/24)} días"
    except:
        return "Reciente"

# --- ESTRUCTURA DE LA APLICACIÓN ---

# Título Principal
st.markdown("<h1 style='display: flex; align-items: center;'><span style='font-size: 1.2em; margin-right: 15px;'>🚛</span> Retorno Match VIP</h1>", unsafe_allow_html=True)
st.markdown("<h3>Gestión Logística Profesional</h3>", unsafe_allow_html=True)

df_cargas, df_choferes = cargar_datos()

# Generar listas únicas para filtros
opciones_origen = ["TODOS"]
opciones_equipos = []
if not df_cargas.empty and len(df_cargas.columns) > 1:
    opciones_origen += sorted(list(set([str(x).upper().strip() for x in df_cargas.iloc[:, 1] if str(x).strip()])))
if not df_choferes.empty and len(df_choferes.columns) > 3:
    opciones_equipos = sorted(list(set([str(x).title().strip() for x in df_choferes.iloc[:, 3] if str(x).strip()])))

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### Filtros de Búsqueda")
    
    st.markdown("<p style='font-size: 14px; margin-bottom: 5px; color: #a0aec0;'>Origen</p>", unsafe_allow_html=True)
    filtro_origen = st.selectbox("", opciones_origen, label_visibility="collapsed")
    
    st.markdown("<p style='font-size: 14px; margin-bottom: 5px; margin-top: 15px; color: #a0aec0;'>Tipo de Equipo</p>", unsafe_allow_html=True)
    filtro_equipo = st.multiselect("", opciones_equipos, label_visibility="collapsed", placeholder="Choose options")
    
    st.markdown("---")
    st.markdown("### 🔧 Panel de Control")
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- ÁREA PRINCIPAL DE TARJETAS ---
tabs = st.tabs(["📦 Cargas Disponibles", "🚚 Camiones Disponibles"])

# PESTAÑA 1: CARGAS
with tabs[0]:
    if df_cargas.empty:
        st.info("No hay datos cargados en la base de datos de Cargas.")
    else:
        # Invertir para ver lo más nuevo primero
        for idx in range(len(df_cargas) - 1, -1, -1):
            row = df_cargas.iloc[idx]
            if len(row) < 5: continue
            
            # Mapeo por índice (0:Marca temporal, 1:Origen, 2:Destino, 3:Mercaderia, 4:Contacto/Wsp)
            timestamp = str(row.iloc[0])
            origen = str(row.iloc[1]).upper().strip()
            destino = str(row.iloc[2]).upper().strip()
            mercaderia = str(row.iloc[3]).title().strip()
            contacto = str(row.iloc[4]).strip()
            empresa = str(row.iloc[5]).title().strip() if len(row) > 5 else "A Confirmar"
            
            if not origen or origen == "NAN": continue
            if filtro_origen != "TODOS" and filtro_origen not in origen: continue
            
            tiempo_str = calcular_tiempo_transcurrido(timestamp)
            wsp_limpio = limpiar_telefono(contacto)
            
            msg = urllib.parse.quote(f"Hola, te escribo desde el sistema Retorno Match. Me interesa la carga de {mercaderia} que publicaste de {origen} hacia {destino}. ¿Sigue disponible?")
            enlace_wsp = f"https://wa.me/{wsp_limpio}?text={msg}" if wsp_limpio else "#"

            st.markdown(f"""
            <div class="match-card">
                <div>
                    <span class="badge-disponible">DISPONIBLE</span>
                    <span class="badge-tiempo">🕒 {tiempo_str}</span>
                </div>
                <div class="ruta-texto">{origen} ➔ {destino}</div>
                <div class="info-texto"><span class="info-icon">📦</span> <b>Carga:&nbsp;</b> {mercaderia}</div>
                <div class="info-texto"><span class="info-icon">🏢</span> <b>Empresa:&nbsp;</b> {empresa}</div>
                <div class="info-texto"><span class="info-icon">📱</span> <b>Contacto:&nbsp;</b> {contacto}</div>
                <a href="{enlace_wsp}" target="_blank" class="btn-whatsapp">
                    <span style="color: #25D366; font-size: 1.2em; vertical-align: middle;">📞</span> Contactar por WhatsApp
                </a>
            </div>
            """, unsafe_allow_html=True)

# PESTAÑA 2: CAMIONES
with tabs[1]:
    if df_choferes.empty:
        st.info("No hay datos cargados en la base de datos de Camiones.")
    else:
        for idx in range(len(df_choferes) - 1, -1, -1):
            row = df_choferes.iloc[idx]
            if len(row) < 5: continue
            
            # Mapeo por índice (0:Marca temporal, 1:Origen, 2:Destino, 3:Equipo, 4:ID/CUIT, 5:Wsp)
            timestamp = str(row.iloc[0])
            origen = str(row.iloc[1]).upper().strip()
            destino = str(row.iloc[2]).upper().strip()
            equipo = str(row.iloc[3]).title().strip()
            
            if not origen or origen == "NAN": continue
            if filtro_origen != "TODOS" and filtro_origen not in origen: continue
            if filtro_equipo and equipo not in filtro_equipo: continue
            
            wsp_raw = str(row.iloc[5]) if len(row) > 5 else str(row.iloc[4])
            wsp_limpio = limpiar_telefono(wsp_raw)
            tiempo_str = calcular_tiempo_transcurrido(timestamp)
            
            msg = urllib.parse.quote(f"Hola, te contacto por tu camión ({equipo}) publicado en Retorno Match desde {origen} a {destino}. Tengo un viaje para ofrecerte.")
            enlace_wsp = f"https://wa.me/{wsp_limpio}?text={msg}" if wsp_limpio else "#"

            st.markdown(f"""
            <div class="match-card" style="border-left-color: #3498db;">
                <div>
                    <span class="badge-disponible" style="background-color: #3498db; color: white;">CAMIÓN LIBRE</span>
                    <span class="badge-tiempo">🕒 {tiempo_str}</span>
                </div>
                <div class="ruta-texto">{origen} ➔ {destino}</div>
                <div class="info-texto"><span class="info-icon">🚛</span> <b>Equipo:&nbsp;</b> {equipo}</div>
                <div class="info-texto"><span class="info-icon">📱</span> <b>Contacto:&nbsp;</b> {wsp_raw}</div>
                <a href="{enlace_wsp}" target="_blank" class="btn-whatsapp">
                    <span style="color: #25D366; font-size: 1.2em; vertical-align: middle;">📞</span> Ofrecer Viaje
                </a>
            </div>
            """, unsafe_allow_html=True)

# --- PIE DE PÁGINA BLINDADO ---
st.markdown("""
<div class="footer-legal">
    <span class="creator-name">CREADO POR IGNACIO DIAZ</span><br>
    Sistema de Gestión de Acopio y Logística<br>
    © 2026 Todos los derechos reservados.
</div>
""", unsafe_allow_html=True)
