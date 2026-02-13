import streamlit as st
import pandas as pd
import urllib.parse
import time

# 1. CONFIGURACIÓN DE PÁGINA (Pestaña del navegador)
st.set_page_config(page_title="RETORNO MATCH | Logística San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS PROFESIONAL (Interfaz estilo Dashboard)
st.markdown("""
    <style>
    /* Fondo principal con overlay oscuro */
    .stApp {
        background: linear-gradient(rgba(10, 20, 30, 0.9), rgba(10, 20, 30, 0.9)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }

    /* Títulos y textos */
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    p { color: #d1d1d1 !important; }

    /* Estilo de la Tarjeta del Camión */
    .camion-card {
        background: rgba(255, 255, 255, 1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        border-left: 8px solid #25D366;
        transition: transform 0.2s;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .camion-card:hover {
        transform: translateY(-5px);
    }

    /* Contenido de la tarjeta */
    .info-container { flex-grow: 1; }
    .route-text {
        font-size: 24px;
        font-weight: 800;
        color: #1a1a1a !important;
        margin-bottom: 5px;
        text-transform: uppercase;
    }
    .details-text {
        color: #555555 !important;
        font-size: 16px;
        font-weight: 500;
        display: flex;
        gap: 20px;
    }
    .date-text {
        color: #999999 !important;
        font-size: 12px;
        margin-top: 10px;
    }

    /* Botón WhatsApp */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 14px 28px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 16px;
        display: inline-block;
        transition: background 0.3s;
        text-align: center;
    }
    .btn-wa:hover { background-color: #128C7E; }

    /* Ajuste para el expander del formulario */
    .stExpander {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
col_logo, col_title = st.columns([1, 5])
with col_title:
    st.markdown("<h1 style='margin-bottom: 0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #25D366 !important; font-weight: 600; font-size: 1.2rem; margin-top: -10px;'>LOGÍSTICA SAN JORGE — CONECTANDO EL TRANSPORTE</p>", unsafe_allow_html=True)

st.write("---")

# 4. FORMULARIO INTEGRADO (EXPANDER PROFESIONAL)
with st.expander("📝 PUBLICAR MI CAMIÓN DISPONIBLE"):
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform?embedded=true"
    st.components.v1.iframe(LINK_FORM, height=600, scrolling=True)
    st.markdown("<p style='text-align:center; font-size:0.9rem;'>Luego de enviar, pulsá 'Actualizar Listado' debajo.</p>", unsafe_allow_html=True)

# 5. CONEXIÓN A DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

try:
    df = pd.read_csv(URL)
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    df = df.dropna(subset=['origen'])

    # 6. PANEL DE CONTROL (Buscador y Refresh)
    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("", placeholder="🔍 Buscar por origen o destino (ej: Rosario, Córdoba...)")
    with c2:
        if st.button("🔄 ACTUALIZAR DATOS", use_container_width=True):
            st.rerun()

    # 7. RENDERIZADO DE VIAJES
    if not df.empty:
        # Filtro de búsqueda
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        # Mostrar tarjetas (de más reciente a más antigua)
        for _, row in df.iloc[::-1].iterrows():
            tel_limpio = "".join(filter(str.isdigit, str(row['tel'])))
            msg = urllib.parse.quote(f"Hola! Vi tu camion de {row['origen']} a {row['destino']} en Retorno Match. ¿Seguís disponible?")
            link_wa = f"https://wa.me/{tel_limpio}?text={msg}"
            
            # HTML de la tarjeta profesional
            st.markdown(f"""
            <div class="camion-card">
                <div class="info-container">
                    <div class="route-text">📍 {row['origen']} → {row['destino']}</div>
                    <div class="details-text">
                        <span>🚛 <b>EQUIPO:</b> {str(row['equipo']).upper()}</span>
                    </div>
                    <div class="date-text">📅 Publicado: {row['fecha']}</div>
                </div>
                <div style="min-width: 150px; text-align: right;">
                    <a href="{link_wa}" target="_blank" class="btn-wa">📱 CONTACTAR</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Esperando nuevos registros de camiones...")

except Exception as e:
    st.warning("Cargando base de datos...")

# PIE DE PÁGINA
st.markdown("<br><hr><p style='text-align:center; color:#555 !important;'>San Jorge, Santa Fe | Gestión Logística 2026</p>", unsafe_allow_html=True)
