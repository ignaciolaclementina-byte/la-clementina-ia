import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 Verificá tu unidad para aparecer primero -- Creado por Ignacio Diaz"

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 3. ESTILOS BLINDADOS ---
st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .radar-container {
        background: rgba(231, 76, 60, 0.9);
        color: white; padding: 10px; border-radius: 10px;
        margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f;
    }
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; }
    .card-premium { background: #fffcf0 !important; border: 2.5px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #f1c40f !important; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.4); }
    .footer { text-align: center; color: white; padding: 40px; font-size: 12px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 70px !important; background-color: #2c3e50 !important; color: white !important; font-size: 18px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 4. MOTOR DE LÓGICA ---
def limpiar_lista(texto):
    items = [s.strip().upper() for s in texto.split(",") if s.strip()]
    return ", ".join(sorted(list(set(items))))

def es_verificado(dato):
    lista = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista

# (Carga de datos simplificada para el ejemplo, mantiene tu conexión real)
try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch_raw, df_ca_raw = pd.DataFrame(), pd.DataFrame()

# --- 5. RADAR ---
st.markdown(f"""<div class="radar-container"><marquee scrollamount="8">🔥 {st.session_state.anuncios} -- 🚛 Creado por Ignacio Diaz.</marquee></div>""", unsafe_allow_html=True)

# (Sección de búsqueda y pestañas se mantiene igual que tu versión funcional)
t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ... (Aquí va el código de visualización de tarjetas de la versión anterior) ...

# --- 7. PANEL DE CONTROL (ADMINISTRACIÓN RÁPIDA) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (GESTOR DE SOCIOS)"):
    
    # SECCIÓN 1: BAJA RÁPIDA
    st.subheader("❌ Quitar Socio (Baja Rápida)")
    c_baja1, c_baja2 = st.columns([3, 1])
    con_quien = c_baja1.text_input("Ingresá CUIT o Nombre a eliminar:")
    if c_baja2.button("BORRAR AHORA", use_container_width=True):
        actuales = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
        objetivo = con_quien.strip().upper()
        if objetivo in actuales:
            actuales.remove(objetivo)
            st.session_state.socios_activos = ", ".join(actuales)
            st.success(f"✅ {objetivo} eliminado correctamente.")
            time.sleep(1)
            st.rerun()
        else:
            st.error("No se encontró ese socio en la lista.")

    st.markdown("---")
    
    # SECCIÓN 2: CARGA MASIVA Y RADAR
    st.subheader("📝 Gestión General")
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        an_txt = st.text_area("Anuncios del Radar:", st.session_state.anuncios, height=100)
    with col_adm2:
        soc_txt = st.text_area("Lista completa de Socios (CUIT o Nombre):", st.session_state.socios_activos, height=100)
    
    if st.button("🚀 GUARDAR CAMBIOS GENERALES", use_container_width=True):
        st.session_state.anuncios = an_txt
        st.session_state.socios_activos = limpiar_lista(soc_txt)
        st.success("¡Base de datos actualizada!"); time.sleep(1); st.rerun()

# --- 8. FOOTER ---
st.markdown(f"""<div class="footer"><p>Desarrollado por <b>Ignacio Diaz</b></p><div style="font-size: 10px; color: rgba(255,255,255,0.5);">AVISO LEGAL: PROHIBIDA LA RÉPLICA TOTAL O PARCIAL. Creado por Ignacio Diaz y sus legales.</div></div>""", unsafe_allow_html=True)
