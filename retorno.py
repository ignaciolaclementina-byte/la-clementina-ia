import streamlit as st
import pandas as pd
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO VISUAL (Fondo de depósito y tarjetas limpias)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
    }
    .stApp, [data-testid="stHeader"] { background: transparent !important; }
    
    .card-container {
        background: white !important;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .route-text { font-size: 18px; font-weight: bold; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 13px; color: #666 !important; margin: 0; }
    
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 8px 16px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. DATOS TÉCNICOS (Tu Formulario Único)
URL_GOOGLE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/formResponse"
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"

# IDs que sacamos de tu link
ID_ORIGEN = "entry.973040585"
ID_DESTINO = "entry.1801965341"
ID_EQUIPO_MERC = "entry.661385730"
ID_TEL = "entry.118433459"

# 4. HEADER
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366; font-weight:bold; margin-top:-20px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- VISTA CHOFER ---
with tab1:
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.subheader("📢 Publicar mi Camión")
        with st.form("form_camion", clear_on_submit=True):
            orig = st.text_input("📍 ¿Desde dónde salís?")
            dest = st.text_input("🏁 ¿Hacia dónde vas?")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Todo los Equipos"])
            tel = st.text_input("📱 WhatsApp (Solo números)")
            
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                payload = {ID_ORIGEN: orig, ID_DESTINO: dest, ID_EQUIPO_MERC: f"CAMION: {equi}", ID_TEL: tel}
                requests.post(URL_GOOGLE_FORM, data=payload)
                st.success("✅ ¡Publicado! Ya aparecés en la lista.")
                time.sleep(1)
                st.rerun()

    with col_f2:
        st.subheader("📦 Cargas que esperan transporte")
        # Leemos la hoja de respuestas
        URL_CSV = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&t={int(time.time())}"
        try:
            df = pd.read_csv(URL_CSV)
            # Filtramos solo lo que diga "CARGA:" en la columna equipo/mercadería
            df_cargas = df[df.iloc[:, 3].str.contains("CARGA:", na=False)]
            for _, row in df_cargas.iloc[::-1].head(10).iterrows():
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #3498db;">
                        <div>
                            <p class="route-text">📍 {str(row.iloc[1]).upper()} ➔ {str(row.iloc[2]).upper()}</p>
                            <p class="detail-text">{row.iloc[3]} | 📅 {row.iloc[0]}</p>
                        </div>
                        <a href="https://wa.me/{row.iloc[4]}" target="_blank" class="btn-wa" style="background-color:#3498db;">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("No hay cargas publicadas por ahora.")

# --- VISTA EMPRESA ---
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.subheader("📢 Publicar Carga")
        with st.form("form_carga", clear_on_submit=True):
            e_orig = st.text_input("📍 Punto de Retiro")
            e_dest = st.text_input("🏁 Punto de Entrega")
            e_merc = st.text_input("📦 ¿Qué mercadería es?")
            e_tel = st.text_input("📱 WhatsApp Empresa")
            
            if st.form_submit_button("BUSCAR CAMIÓN AHORA", use_container_width=True):
                payload = {ID_ORIGEN: e_orig, ID_DESTINO: e_dest, ID_EQUIPO_MERC: f"CARGA: {e_merc}", ID_TEL: e_tel}
                requests.post(URL_GOOGLE_FORM, data=payload)
                st.success("✅ ¡Carga publicada con éxito!")
                time.sleep(1)
                st.rerun()

    with col_e2:
        st.subheader("🚛 Camiones buscando retorno")
        try:
            df = pd.read_csv(URL_CSV)
            # Filtramos solo lo que diga "CAMION:"
            df_camiones = df[df.iloc[:, 3].str.contains("CAMION:", na=False)]
            for _, row in df_camiones.iloc[::-1].head(10).iterrows():
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #25D366;">
                        <div>
                            <p class="route-text">📍 {str(row.iloc[1]).upper()} ➔ {str(row.iloc[2]).upper()}</p>
                            <p class="detail-text">{row.iloc[3]} | 📅 {row.iloc[0]}</p>
                        </div>
                        <a href="https://wa.me/{row.iloc[4]}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("No hay camiones buscando retorno ahora.")
