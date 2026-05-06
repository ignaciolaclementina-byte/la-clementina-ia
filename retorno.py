import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN DE ESTRUCTURA NACHO (BLINDADA) ---
# Se mantiene la vinculación exacta a tu base de datos
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

# --- 2. FUNCIONES DE LIMPIEZA DE DATOS (SIN COMAS NI DECIMALES) ---
def limpiar_numero_vistas(dato):
    """Elimina comas y decimales (.0) de códigos, CUITs y teléfonos"""
    if pd.isna(dato) or dato == "-": return "-"
    # Convierte a string, quita el .0 y cualquier coma de formato
    return str(dato).split('.')[0].replace(',', '').strip()

def format_whatsapp(numero, mensaje):
    """Genera link de WhatsApp con mensaje profesional"""
    num_limpio = "".join(filter(str.isdigit, str(numero)))
    if not num_limpio.startswith("54"):
        num_limpio = "54" + num_limpio
    msg_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{num_limpio}?text={msg_encoded}"

# --- 3. CARGA DE DATOS (MANTIENE INTERFAZ ACTUAL) ---
@st.cache_data(ttl=10)
def cargar_datos():
    t = int(time.time())
    url_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
    url_ca = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
    
    df_ch = pd.read_csv(url_ch).fillna("-")
    df_ca = pd.read_csv(url_ca).fillna("-")
    
    # Filtrado preventivo de filas marcadas como BORRADO
    df_ca = df_ca[~df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)]
    
    return df_ch, df_ca

# --- 4. INTERFAZ VISUAL (MANTIENE TU DISEÑO ORIGINAL) ---
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# Estilos idénticos a tu versión actual
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
        border-left: 5px solid #007bff;
    }
    .footer { text-align: center; color: #666; padding: 20px; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH - San Jorge")
st.subheader("Gestión de Cargas y Retornos en Tiempo Real")

df_ch, df_ca = cargar_datos()

# Filtros de búsqueda (Interfaz estándar)
col1, col2 = st.columns(2)
with col1:
    origen_f = st.text_input("📍 Ciudad Origen").upper()
with col2:
    destino_f = st.text_input("🏁 Ciudad Destino").upper()

tab1, tab2 = st.tabs(["📦 CARGAS DISPONIBLES", "🚛 CHOFERES DISPONIBLES"])

# --- TAB CARGAS ---
with tab1:
    filt_ca = df_ca[(df_ca.iloc[:,1].str.upper().str.contains(origen_f)) & 
                    (df_ca.iloc[:,2].str.upper().str.contains(destino_f))]
    
    for i, r in filt_ca.iterrows():
        tel = limpiar_numero_vistas(r[4])
        # Mensaje de WhatsApp mejorado y profesional
        msj = f"Hola, me contacto por la carga de {r[1]} a {r[2]} ({r[3]}) vista en Retorno Match."
        
        st.markdown(f"""
        <div class="card">
            <h4>{r[1]} ➔ {r[2]}</h4>
            <p><b>Carga:</b> {r[3]} | <b>Empresa:</b> {r[5]}</p>
            <p><b>Contacto:</b> {tel}</p>
            <a href="{format_whatsapp(tel, msj)}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">
                    💬 POSTULARME POR WHATSAPP
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- TAB CHOFERES ---
with tab2:
    filt_ch = df_ch[(df_ch.iloc[:,1].str.upper().str.contains(origen_f)) & 
                    (df_ch.iloc[:,2].str.upper().str.contains(destino_f))]
    
    for i, r in filt_ch.iterrows():
        cuit = limpiar_numero_vistas(r[4])
        tel = limpiar_numero_vistas(r[5])
        msj_chofer = f"Hola, te escribo por tu equipo {r[3]} que está en {r[1]} con destino {r[2]}."
        
        st.markdown(f"""
        <div class="card" style="border-left-color: #28a745;">
            <h4>Chofer en {r[1]} para {r[2]}</h4>
            <p><b>Equipo:</b> {r[3]} | <b>CUIT:</b> {cuit}</p>
            <a href="{format_whatsapp(tel, msj_chofer)}" target="_blank" style="text-decoration:none;">
                <button style="width:100%; background-color:#007bff; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">
                    📞 CONTACTAR TRANSPORTE
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO) ---
st.markdown("---")
st.markdown(f"""
    <div class="footer">
        <b>Creado por Ignacio Diaz</b><br>
        © {datetime.now().year} Retorno Match - Estructura Nacho Blindada<br>
        <i>Software de Gestión Logística de Alta Eficiencia</i>
    </div>
    """, unsafe_allow_html=True)
