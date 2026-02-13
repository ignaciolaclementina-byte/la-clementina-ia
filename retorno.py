import streamlit as st
import pandas as pd
import time
import requests

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. CSS AVANZADO (Mantenemos tu estilo de cristal)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .stApp, .stMain, [data-testid="stHeader"] { background: transparent !important; }
    
    /* Estilo de Tarjetas */
    .card-container {
        background: white !important;
        border-radius: 15px;
        padding: 18px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .detail-text { font-size: 14px; color: #555 !important; }
    
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
    }

    /* Formularios */
    .stForm {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 15px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. FUNCIÓN PARA ENVIAR DATOS A GOOGLE (Sustituye al Formulario Externo)
def enviar_a_google(url_form, datos):
    try:
        requests.post(url_form, data=datos)
        return True
    except:
        return False

# 4. HEADER
st.markdown("""
    <div style='text-align:center; padding-bottom: 20px;'>
        <h1 style='font-size: 45px; color: white; margin-bottom:0;'>🚛 RETORNO MATCH</h1>
        <p style='color: #25D366; font-size: 18px; font-weight: bold; letter-spacing: 2px;'>LOGÍSTICA PROFESIONAL SAN JORGE</p>
    </div>
    """, unsafe_allow_html=True)

# IDs de tus formularios (Los sacamos de la URL de 'enviar' de Google Forms)
# Necesitaremos los IDs de los campos (entry.12345) para que sea automático
FORM_CAMIONES_URL = "https://docs.google.com/forms/d/e/TU_ID_FORM_3/formResponse"
FORM_CARGAS_URL = "https://docs.google.com/forms/d/e/1wyj2NyletifL_9OYphSFNrZRA38l6fLe2TNNg95pJxc/formResponse"

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- VISTA CHOFER ---
with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_chofer", clear_on_submit=True):
            f_orig = st.text_input("📍 Origen")
            f_dest = st.text_input("🏁 Destino")
            f_equi = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            f_tel = st.text_input("📱 WhatsApp (con código de área)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD", use_container_width=True):
                # Aquí conectaremos los entry.id de tu Google Form 3
                st.success("¡Publicado! Aparecerás en la lista de empresas.")

    with col_b:
        st.markdown("### 📦 Cargas disponibles")
        # Lectura de Hoja 4
        SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
        URL_C = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%204&t={int(time.time())}"
        try:
            df_c = pd.read_csv(URL_C).iloc[:, :5]
            df_c.columns = ['fecha', 'origen', 'destino', 'mercaderia', 'tel']
            for _, row in df_c.iloc[::-1].head(10).iterrows():
                st.markdown(f"""
                    <div class="card-container" style="border-left: 10px solid #3498db;">
                        <div class="info-section">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">📦 {row['mercaderia']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{row['tel']}" class="btn-wa" style="background-color: #3498db;">ACEPTAR</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando nuevas cargas...")

# --- VISTA EMPRESA ---
with tab2:
    col_c, col_d = st.columns([1, 2])
    with col_c:
        st.markdown("### 📢 Publicar Carga")
        with st.form("form_empresa", clear_on_submit=True):
            e_orig = st.text_input("📍 Punto de Retiro")
            e_dest = st.text_input("🏁 Punto de Entrega")
            e_merc = st.text_input("📦 Mercadería")
            e_tel = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("BUSCAR CAMIÓN AHORA", use_container_width=True):
                # Aquí conectaremos los entry.id de tu Google Form 4
                st.success("¡Carga publicada! Los choferes ya pueden verla.")

    with col_d:
        st.markdown("### 🚛 Camiones buscando retorno")
        # Lectura de Hoja 3
        URL_V = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
        try:
            df_v = pd.read_csv(URL_V).iloc[:, :5]
            df_v.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
            for _, row in df_v.iloc[::-1].head(10).iterrows():
                st.markdown(f"""
                    <div class="card-container" style="border-left: 10px solid #25D366;">
                        <div class="info-section">
                            <p class="route-text">📍 {str(row['origen']).upper()} ➔ {str(row['destino']).upper()}</p>
                            <p class="detail-text">🚛 {row['equipo']} | 📅 {row['fecha']}</p>
                        </div>
                        <a href="https://wa.me/{row['tel']}" class="btn-wa">WHATSAPP</a>
                    </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando camiones...")
