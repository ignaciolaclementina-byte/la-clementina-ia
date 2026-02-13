import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS PARA UNA INTERFAZ DE ALTO NIVEL
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    
    /* Tarjetas de Camiones */
    .camion-card {
        background: #ffffff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        border-left: 10px solid #25D366;
    }
    .route-text { font-size: 22px; font-weight: 800; color: #1a1a1a; margin: 0; }
    .detail-text { color: #444; font-size: 15px; margin: 5px 0; }
    
    /* Botón WhatsApp */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Input de búsqueda y botones */
    .stTextInput > div > div > input { background-color: #1e212b; color: white; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 3. ENCABEZADO MODERNO
st.markdown("<h1 style='text-align:center; color:white; font-size: 45px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366; font-weight:bold; margin-top:-15px;'>LOGÍSTICA SAN JORGE — CONECTANDO CARGAS</p>", unsafe_allow_html=True)

# 4. FORMULARIO INTEGRADO (NATIVO DE STREAMLIT)
with st.expander("➕ PUBLICAR MI CAMIÓN (Cargar datos aquí)"):
    with st.form("form_carga", clear_on_submit=True):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            origen = st.text_input("📍 Ciudad de Origen", placeholder="Ej: Rosario")
            equipo = st.selectbox("🚛 Tipo de Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
        with col_f2:
            destino = st.text_input("🏁 Ciudad de Destino", placeholder="Ej: San Jorge")
            whatsapp = st.text_input("📱 Tu WhatsApp (Solo números)", placeholder="3406123456")
        
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA", use_container_width=True)
        
        if enviar:
            if origen and destino and whatsapp:
                # URL de envío de Google Forms (Pre-filled URL)
                # Reemplaza los IDs de entrada con los de tu formulario real
                FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/formResponse"
                payload = {
                    "entry.1834914102": origen,   # Cambiar por ID real del campo Origen
                    "entry.1121303831": destino,  # Cambiar por ID real del campo Destino
                    "entry.1018903264": equipo,   # Cambiar por ID real del campo Equipo
                    "entry.1437637841": whatsapp  # Cambiar por ID real del campo WhatsApp
                }
                try:
                    requests.post(FORM_URL, data=payload)
                    st.success("¡Camión publicado con éxito! Dale a 'Actualizar' para verlo.")
                except:
                    st.error("Error al conectar. Intenta de nuevo.")
            else:
                st.warning("Por favor, completa todos los campos.")

st.divider()

# 5. LISTADO DE VIAJES
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

try:
    df = pd.read_csv(URL)
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    df = df.dropna(subset=['origen'])

    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("", placeholder="🔍 Buscar por ciudad o equipo...")
    with c2:
        if st.button("🔄 ACTUALIZAR LISTADO", use_container_width=True):
            st.rerun()

    if not df.empty:
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False) |
                    df['equipo'].str.contains(search, case=False, na=False)]

        for _, row in df.iloc[::-1].iterrows():
            tel = "".join(filter(str.isdigit, str(row['tel'])))
            link_wa = f"https://wa.me/{tel}?text=Hola!%20Vi%20tu%20camion%20en%20Retorno%20Match"
            
            st.markdown(f"""
            <div class="camion-card">
                <div>
                    <p class="route-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                    <p class="detail-text"><b>EQUIPO:</b> {row['equipo']} | <b>FECHA:</b> {row['fecha']}</p>
                </div>
                <a href="{link_wa}" target="_blank" class="btn-wa">📱 WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay camiones disponibles en este momento.")

except Exception:
    st.error("Error cargando datos. Verifique la conexión.")
