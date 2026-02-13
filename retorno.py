import streamlit as st
import pandas as pd
import urllib.parse
import time

# --- NUEVO: Función para auto-refrescar cada 2 minutos ---
def autorefresh(interval_seconds):
    time.sleep(interval_seconds)
    st.rerun()

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO VISUAL PREMIUM
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    .camion-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content h3 { color: #1a1a1a; margin: 0 0 5px 0; font-size: 24px; font-weight: 800; }
    .card-content p { color: #555; margin: 0; font-size: 16px; }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO PRINCIPAL
st.markdown("<h1 style='text-align:center; color:white; font-size: 55px; font-weight: 900; margin-bottom: 0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00FF41; font-size: 18px; margin-top: -10px;'>LOGÍSTICA SAN JORGE - CONECTANDO CARGAS</p>", unsafe_allow_html=True)
st.write("---")

# 3. CONEXIÓN A LA BASE DE DATOS (Truco anti-cache)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

try:
    df = pd.read_csv(URL)
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    df = df.dropna(subset=['origen'])

    # 4. BUSCADOR Y BOTÓN DE CARGA
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search = st.text_input("", placeholder="🔍 Buscar ciudad...")
    with col_btn:
        LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform?usp=header"
        st.link_button("➕ CARGAR CAMIÓN", LINK_FORM, use_container_width=True)

    # 5. MOSTRAR TARJETAS
    if not df.empty:
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        for _, row in df.iloc[::-1].iterrows():
            tel_limpio = "".join(filter(str.isdigit, str(row['tel'])))
            texto = f"Hola! Vi tu camion de {row['origen']} a {row['destino']} en Retorno Match."
            link_wa = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(texto)}"
            
            st.markdown(f"""
            <div class="camion-card">
                <div class="card-content">
                    <h3>📍 {str(row['origen']).upper()} ➝ {str(row['destino']).upper()}</h3>
                    <p>🚛 <b>Equipo:</b> {row['equipo']}</p>
                    <p style="font-size: 12px; color: #999; margin-top: 5px;">📅 Publicado: {row['fecha']}</p>
                </div>
                <div>
                    <a href="{link_wa}" target="_blank" class="btn-wa">📱 WHATSAPP</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:white;'>No hay camiones reportados.</h3>", unsafe_allow_html=True)

except Exception as e:
    st.info("Sincronizando...")

st.markdown("<br><br><p style='text-align:center; color:gray; font-size:12px;'>San Jorge, Santa Fe - 2026</p>", unsafe_allow_html=True)

# 6. ACTIVAR EL AUTO-REFRESCO AL FINAL (120 segundos)
# Nota: Esto hará que la App se refresque sola.
# autorefresh(120)
