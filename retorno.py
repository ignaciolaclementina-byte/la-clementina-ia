import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse  # Para codificar el texto del mensaje

# --- 1. CONFIGURACIÓN DE CONEXIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

# URL y Entry IDs de Formularios de Google
FORM_CHOFER_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH_ORIGEN, ID_CH_DESTINO, ID_CH_EQUIPO, ID_CH_TEL = "entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"

FORM_EMPRESA_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM_ORIGEN, ID_EM_DESTINO, ID_EM_MERC, ID_EM_TEL = "entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450"

# --- 2. CONFIGURACIÓN DE PÁGINA Y ESTILO (UI/UX) ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

st.markdown("""
    <style>
    /* Fondo principal con overlay oscuro */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp { background: transparent !important; }
    
    /* Tarjetas de listado */
    .card-container {
        background: white !important; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 14px; color: #555 !important; margin: 4px 0 0 0; }
    
    /* Botón de WhatsApp estilo original */
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 14px; }
    .btn-wa:hover { background-color: #128C7E; color: white !important; }
    
    /* Formulario efecto Cristal */
    .stForm { background: rgba(255, 255, 255, 0.08) !important; border: 1px solid rgba(255, 255, 255, 0.2) !important; border-radius: 15px !important; padding: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Función para enviar datos a Google Forms sin redirigir
def enviar_a_google(url, payload):
    try:
        requests.post(url, data=payload, headers={'User-Agent': 'Mozilla/5.0'})
        return True
    except: return False

# Título de la App
st.markdown("<div style='text-align:center; padding-bottom: 20px;'><h1 style='font-size: 48px; margin-bottom:0;'>🚛 RETORNO MATCH</h1><p style='color: #25D366 !important; font-weight: bold; letter-spacing: 2px;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

# Tabs de navegación
tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ==========================================
# PESTAÑA 1: VISTA CHOFER (Busca Carga)
# ==========================================
with tab1:
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_chofer", clear_on_submit=True):
            orig = st.text_input("📍 Origen (¿Dónde estás?)")
            dest = st.text_input("🏁 Destino (¿A dónde vas?)")
            equi = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Sider c/ Plataforma"])
            tel = st.text_input("📱 Tu WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                if orig and dest and tel:
                    if enviar_a_google(FORM_CHOFER_URL, {ID_CH_ORIGEN: orig, ID_CH_DESTINO: dest, ID_CH_EQUIPO: equi, ID_CH_TEL: tel}):
                        st.success("✅ ¡Publicado correctamente!")
                        time.sleep(1.2); st.rerun()
                else:
                    st.warning("Completá todos los campos.")

    with col_f2:
        st.markdown("### 📦 Cargas Disponibles (Publicadas por Empresas)")
        try:
            # Lee la hoja de Cargas
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}")
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            for _, row in df_c.iloc[::-1].head(15).iterrows():
                # Lógica de Limpieza de Teléfono
                t_clean = "".join(filter(str.isdigit, str(row['tel'])))
                if t_clean.startswith('0'): t_clean = t_clean[1:]
                t_final = t_clean if t_clean.startswith('549') else "549" + t_clean
                
                # Mensaje automático para la Empresa
                msg = urllib.parse.quote(f"Hola! Vi tu carga en Retorno Match: {row['origen']} -> {row['destino']} ({row['mercaderia']}). Sigue disponible?")
                
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #3498db;">
                        <div style="flex-grow:1;">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">📦 <b>Carga:</b> {row['mercaderia']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{t_final}?text={msg}" target="_blank" class="btn-wa" style="background-color: #3498db;">TOMAR CARGA</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando cargas...")

# ==========================================
# PESTAÑA 2: VISTA EMPRESA (Busca Camión)
# ==========================================
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.markdown("### 📢 Publicar Nueva Carga")
        with st.form("form_empresa", clear_on_submit=True):
            eo = st.text_input("📍 Punto de Retiro")
            ed = st.text_input("🏁 Punto de Entrega")
            em = st.text_input("📦 Mercadería")
            et = st.text_input("📱 WhatsApp de Contacto")
            if st.form_submit_button("PUBLICAR CARGA AHORA", use_container_width=True):
                if eo and ed and et:
                    if enviar_a_google(FORM_EMPRESA_URL, {ID_EM_ORIGEN: eo, ID_EM_DESTINO: ed, ID_EM_MERC: em, ID_EM_TEL: et}):
                        st.success("✅ ¡Carga en línea!"); time.sleep(1.2); st.rerun()
                else:
                    st.warning("Completá todos los campos.")

    with col_e2:
        st.markdown("### 🚛 Camiones Disponibles (Esperando Carga)")
        try:
            # Lee la hoja de Choferes
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}")
            df_h.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            for _, row in df_h.iloc[::-1].head(15).iterrows():
                # Lógica de Limpieza de Teléfono
                t_clean = "".join(filter(str.isdigit, str(row['tel'])))
                if t_clean.startswith('0'): t_clean = t_clean[1:]
                t_final = t_clean if t_clean.startswith('549') else "549" + t_clean
                
                # Mensaje automático para el Chofer
                msg_ch = urllib.parse.quote(f"Hola! Vi tu camión disponible en Retorno Match: {row['origen']} -> {row['destino']} (Equipo: {row['equipo']}). Te interesa una carga?")
                
                st.markdown(f"""
                    <div class="card-container" style="border-left: 8px solid #25D366;">
                        <div style="flex-grow:1;">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">🚛 <b>Equipo:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{t_final}?text={msg_ch}" target="_blank" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando camiones...")
