import streamlit as st
import pandas as pd
import urllib.parse
import time

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | Logística San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS PROFESIONAL
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(10, 20, 30, 0.9), rgba(10, 20, 30, 0.9)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }

    /* Títulos */
    .main-title {
        color: #ffffff;
        font-size: 48px;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .sub-title {
        color: #25D366;
        text-align: center;
        font-weight: 600;
        font-size: 16px;
        margin-top: -10px;
        margin-bottom: 30px;
        text-transform: uppercase;
    }

    /* Estilo de la Tarjeta */
    .camion-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 8px solid #25D366;
    }
    
    .route {
        font-size: 22px;
        font-weight: 800;
        color: #1a1a1a;
        margin: 0;
    }
    
    .info {
        color: #666;
        font-size: 14px;
        margin-top: 4px;
    }

    /* Botón WhatsApp */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 24px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 700;
        font-size: 14px;
        transition: 0.3s;
    }
    .btn-wa:hover { background-color: #128C7E; }

    /* Estilo para los botones de Streamlit */
    div.stButton > button {
        background-color: rgba(255,255,255,0.1);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<div class='main-title'>🚛 RETORNO MATCH</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Logística San Jorge — Conectando Cargas</div>", unsafe_allow_html=True)

# 4. PANEL DE ACCIONES (Limpio y horizontal)
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("", placeholder="🔍 Buscar ciudad o destino...")

with col2:
    # Botón para refrescar
    if st.button("🔄 ACTUALIZAR LISTA", use_container_width=True):
        st.rerun()

with col3:
    # Botón para cargar (Abre el link en otra pestaña para no romper la estética)
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform?usp=sf_link"
    st.link_button("➕ CARGAR CAMIÓN", LINK_FORM, use_container_width=True)

st.write("") # Espacio

# 5. LÓGICA DE DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

try:
    df = pd.read_csv(URL)
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    df = df.dropna(subset=['origen'])

    if not df.empty:
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        for _, row in df.iloc[::-1].iterrows():
            tel_limpio = "".join(filter(str.isdigit, str(row['tel'])))
            msg = urllib.parse.quote(f"Hola! Vi tu camion de {row['origen']} a {row['destino']} en Retorno Match. ¿Sigue disponible?")
            link_wa = f"https://wa.me/{tel_limpio}?text={msg}"
            
            st.markdown(f"""
            <div class="camion-card">
                <div>
                    <p class="route">📍 {str(row['origen']).upper()} ➝ {str(row['destino']).upper()}</p>
                    <p class="info">🚛 <b>EQUIPO:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                </div>
                <a href="{link_wa}" target="_blank" class="btn-wa">📱 WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:white;'>No hay camiones reportados.</p>", unsafe_allow_html=True)

except Exception:
    st.info("Sincronizando con la base de datos...")

st.markdown("<br><p style='text-align:center; color:gray; font-size:12px;'>Logística San Jorge - 2026</p>", unsafe_allow_html=True)
