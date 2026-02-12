import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# 2. ESTILO CSS (Fondo de depósito + Tarjetas Pro)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 5px;
        color: white !important;
        font-weight: bold;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2ecc71 !important;
    }
    .card-carga {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 12px solid #2ecc71;
        margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    .card-camion {
        background: #ebf5fb;
        padding: 20px;
        border-radius: 15px;
        border-left: 12px solid #3498db;
        margin-bottom: 15px;
    }
    .card-carga h3, .card-carga p, .card-camion h3, .card-camion p {
        color: #2c3e50 !important;
        margin: 5px 0;
    }
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        font-weight: bold;
        margin-top: 15px;
    }
    h1, h2 { color: white !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 3. LINK DE EXCEL (Tu link de publicación .csv)
URL_CARGAS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# 4. TÍTULO Y PESTAÑAS
st.markdown("<h1>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

t_buscar, t_publicar, t_camiones = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR", "🚛 CAMIONES DISPONIBLES"])

# Lógica de carga de datos
try:
    df = pd.read_csv(URL_CARGAS)
    df.columns = df.columns.str.strip().str.lower()
except:
    df = pd.DataFrame()

# --- PESTAÑA 1: BUSCAR ---
with t_buscar:
    if not df.empty:
        # Filtramos solo las que tienen origen (columna A del Excel)
        viajes = df.dropna(subset=['origen'])
        for _, r in viajes.iterrows():
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "").replace("+", "")
            st.markdown(f"""
            <div class='card-carga'>
                <h3>📍 {str(r['origen']).upper()}</h3>
                <p>📦 <b>Producto:</b> {r.get('item', '-')}</p>
                <p>💰 <b>Pago:</b> ${r.get('pago', '-')}</p>
                <p>📲 <b>Teléfono:</b> {r.get('tel', '-')}</p>
                <a class='btn-ws' href='https://wa.me/549{tel}' target='_blank'>SOLICITAR VIAJE</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No hay cargas disponibles en este momento.")

# --- PESTAÑA 2: PUBLICAR ---
with t_publicar:
    st.markdown("<h2>📤 ¿Querés publicar una carga?</h2>", unsafe_allow_html=True)
    st.write("---")
    st.info("Para que tu carga aparezca en la lista, completá los datos en el Excel compartido o contactanos.")
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.rerun()

# --- PESTAÑA 3: CAMIONES ---
with t_camiones:
    st.markdown("<h2>🚛 Camiones buscando retorno</h2>", unsafe_allow_html=True)
    # Ejemplo de cómo se vería (esto lo podés conectar a otra pestaña del Excel después)
    st.markdown("""
    <div class='card-camion'>
        <h3>🚛 Camión Térmico - Nacho</h3>
        <p>📍 <b>Ubicación actual:</b> Rosario</p>
        <p>🏁 <b>Destino:</b> San Jorge</p>
    </div>
    """, unsafe_allow_html=True)
