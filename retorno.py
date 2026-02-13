import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# IDs de Formularios
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450"]

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# Inicializar estado de "Concretados" si no existe
if 'concretados' not in st.session_state:
    st.session_state.concretados = set()

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    
    .card-container {
        background: white !important; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .card-concretada {
        background: #e0e0e0 !important; opacity: 0.7; border-left: 8px solid #7f8c8d !important;
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .status-dispo { color: #25D366; font-weight: bold; font-size: 14px; }
    .status-conc { color: #e74c3c; font-weight: bold; font-size: 14px; }
    
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: bold; }
    .stForm { background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 15px !important; padding: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def enviar_a_google(url, payload):
    try:
        requests.post(url, data=payload, headers={'User-Agent': 'Mozilla/5.0'})
        return True
    except: return False

def filtrar_solo_hoy(df):
    try:
        df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df['fecha'] >= hace_24hs].copy()
    except:
        return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 48px;'>🚛 RETORNO MATCH</h1><p style='color: #25D366 !important; font-weight: bold;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ==========================================
# PESTAÑA 1: VISTA CHOFER
# ==========================================
with tab1:
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_chofer", clear_on_submit=True):
            orig, dest, equi, tel = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if orig and dest and tel:
                    if enviar_a_google(FORM_CH_URL, {ID_CH[0]: orig, ID_CH[1]: dest, ID_CH[2]: equi, ID_CH[3]: tel}):
                        st.success("✅ ¡Publicado!"); time.sleep(1.2); st.rerun()

    with col_f2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            df_c = filtrar_solo_hoy(df_c)
            
            for i, row in df_c.iloc[::-1].iterrows():
                card_id = f"carga_{i}"
                esta_concretado = card_id in st.session_state.concretados
                
                t_clean = "".join(filter(str.isdigit, str(row['tel'])))
                if t_clean.startswith('0'): t_clean = t_clean[1:]
                t_final = t_clean if t_clean.startswith('549') else "549" + t_clean
                
                msg = urllib.parse.quote(f"Hola! Vi tu carga: {row['origen']} -> {row['destino']}. Sigue disponible?")
                link_wa = f"https://api.whatsapp.com/send?phone={t_final}&text={msg}"
                
                status_html = '<span class="status-conc">● CONCRETADO</span>' if esta_concretado else '<span class="status-dispo">● DISPONIBLE</span>'
                css_clase = "card-container card-concretada" if esta_concretado else "card-container"

                st.markdown(f"""
                    <div class="{css_clase}" style="border-left: 8px solid {'#7f8c8d' if esta_concretado else '#3498db'};">
                        <div style="flex-grow:1;">
                            <p style="color:gray; font-size:12px; margin:0;">{status_html} | 🕒 {row['fecha'].strftime('%H:%M')}</p>
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">📦 {row['mercaderia']}</p>
                        </div>
                        {'<span style="color:gray; font-weight:bold;">Cerrado</span>' if esta_concretado else f'<a href="{link_wa}" target="_blank" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>'}
                    </div>
                """, unsafe_allow_html=True)
                
                if not esta_concretado:
                    if st.button(f"Marcar Concretada", key=card_id):
                        st.session_state.concretados.add(card_id)
                        st.rerun()
        except: st.info("Sincronizando...")

# ==========================================
# PESTAÑA 2: VISTA EMPRESA
# ==========================================
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.markdown("### 📢 Publicar Nueva Carga")
        with st.form("form_empresa", clear_on_submit=True):
            eo, ed, em, et = st.text_input("📍 Retiro"), st.text_input("🏁 Entrega"), st.text_input("📦 Mercadería"), st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if eo and ed and et:
                    if enviar_a_google(FORM_EM_URL, {ID_EM[0]: eo, ID_EM[1]: ed, ID_EM[2]: em, ID_EM[3]: et}):
                        st.success("✅ ¡En línea!"); time.sleep(1.2); st.rerun()

    with col_e2:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            df_h.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            df_h = filtrar_solo_hoy(df_h)
            
            for i, row in df_h.iloc[::-1].iterrows():
                card_id = f"camion_{i}"
                esta_concretado = card_id in st.session_state.concretados
                
                t_clean = "".join(filter(str.isdigit, str(row['tel'])))
                if t_clean.startswith('0'): t_clean = t_clean[1:]
                t_final = t_clean if t_clean.startswith('549') else "549" + t_clean
                
                msg_ch = urllib.parse.quote(f"Hola! Vi tu camión: {row['origen']} -> {row['destino']}. Te interesa una carga?")
                link_wa_ch = f"https://api.whatsapp.com/send?phone={t_final}&text={msg_ch}"
                
                status_html = '<span class="status-conc">● CONCRETADO</span>' if esta_concretado else '<span class="status-dispo">● DISPONIBLE</span>'
                css_clase = "card-container card-concretada" if esta_concretado else "card-container"

                st.markdown(f"""
                    <div class="{css_clase}" style="border-left: 8px solid {'#7f8c8d' if esta_concretado else '#25D366'};">
                        <div style="flex-grow:1;">
                            <p style="color:gray; font-size:12px; margin:0;">{status_html} | 🕒 {row['fecha'].strftime('%H:%M')}</p>
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">🚛 {row['equipo']}</p>
                        </div>
                        {'<span style="color:gray; font-weight:bold;">Cerrado</span>' if esta_concretado else f'<a href="{link_wa_ch}" target="_blank" class="btn-wa">WHATSAPP</a>'}
                    </div>
                """, unsafe_allow_html=True)
                
                if not esta_concretado:
                    if st.button(f"Marcar Concretado", key=card_id):
                        st.session_state.concretados.add(card_id)
                        st.rerun()
        except: st.info("Sincronizando...")
