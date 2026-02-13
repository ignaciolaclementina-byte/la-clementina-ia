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

# IDs de Formularios (Verificá que estos coincidan con tus nuevos formularios)
FORM_CH_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
ID_CH = ["entry.1304806144", "entry.1519265625", "entry.597193898", "entry.1574172378"]

FORM_EM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ID_EM = ["entry.610070407", "entry.170847116", "entry.576675281", "entry.466540450"]

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

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
    .card-concretada { background: #e0e0e0 !important; opacity: 0.7; border-left: 8px solid #7f8c8d !important; }
    .route-text { font-size: 20px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .status-dispo { color: #25D366; font-weight: bold; font-size: 14px; }
    .status-conc { color: #e74c3c; font-weight: bold; font-size: 14px; }
    .btn-wa { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: bold; }
    .stForm { background: rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; padding: 20px !important; }
    h1, h3, p, label { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

def filtrar_solo_hoy(df):
    try:
        # Forzamos la conversión de la primera columna (Marca temporal)
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        hace_24hs = datetime.now() - timedelta(hours=24)
        return df[df.iloc[:, 0] >= hace_24hs].copy()
    except:
        return df

st.markdown("<div style='text-align:center;'><h1 style='font-size: 48px;'>🚛 RETORNO MATCH</h1><p style='color: #25D366 !important; font-weight: bold;'>LOGÍSTICA SAN JORGE</p></div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👋 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# --- LÓGICA DE CARGA DE DATOS ---
def leer_datos(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&t={int(time.time())}"
    return pd.read_csv(url)

# --- PESTAÑA CHOFER ---
with tab1:
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_ch", clear_on_submit=True):
            o = st.text_input("📍 Origen")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
            t = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_CH_URL, data={ID_CH[0]:o, ID_CH[1]:d, ID_CH[2]:e, ID_CH[3]:t})
                st.success("Publicado!"); time.sleep(1); st.rerun()

    with col_f2:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = leer_datos(GID_CARGAS)
            df_c = filtrar_solo_hoy(df_c)
            for i, row in df_c.iloc[::-1].iterrows():
                # Mapeo dinámico por posición de columna para evitar errores de nombre
                fecha, orig, dest, merca, tel = row[0], row[1], row[2], row[3], row[4]
                cid = f"c_{i}"
                conc = cid in st.session_state.concretados
                
                t_clean = "".join(filter(str.isdigit, str(tel)))
                if not t_clean.startswith('54'): t_clean = "549" + t_clean
                link = f"https://api.whatsapp.com/send?phone={t_clean}&text=Hola! Vi tu carga: {orig} a {dest}."

                st.markdown(f"""
                    <div class="card-container {'card-concretada' if conc else ''}">
                        <div style="flex-grow:1;">
                            <p class="status-{'conc' if conc else 'dispo'}">● {'CONCRETADO' if conc else 'DISPONIBLE'}</p>
                            <p class="route-text">📍 {str(orig).upper()} ➔ {str(dest).upper()}</p>
                            <p class="detail-text" style="color:black !important;">📦 {merca}</p>
                        </div>
                        {'' if conc else f'<a href="{link}" target="_blank" class="btn-wa">TOMAR</a>'}
                    </div>
                """, unsafe_allow_html=True)
                if not conc:
                    if st.button("Marcar Concretado", key=cid):
                        st.session_state.concretados.add(cid); st.rerun()
        except Exception as err:
            st.warning("Aún no hay datos cargados o el Excel está privado.")

# --- PESTAÑA EMPRESA ---
with tab2:
    col_e1, col_e2 = st.columns([1, 2])
    with col_e1:
        st.markdown("### 📢 Publicar Carga")
        with st.form("form_em", clear_on_submit=True):
            eo = st.text_input("📍 Retiro")
            ed = st.text_input("🏁 Entrega")
            em = st.text_input("📦 Mercadería")
            et = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(FORM_EM_URL, data={ID_EM[0]:eo, ID_EM[1]:ed, ID_EM[2]:em, ID_EM[3]:et})
                st.success("Publicado!"); time.sleep(1); st.rerun()

    with col_e2:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = leer_datos(GID_CHOFERES)
            df_h = filtrar_solo_hoy(df_h)
            for i, row in df_h.iloc[::-1].iterrows():
                fecha, orig, dest, equi, tel = row[0], row[1], row[2], row[3], row[4]
                mid = f"m_{i}"
                conc = mid in st.session_state.concretados
                
                t_clean = "".join(filter(str.isdigit, str(tel)))
                if not t_clean.startswith('54'): t_clean = "549" + t_clean
                link = f"https://api.whatsapp.com/send?phone={t_clean}&text=Hola! Vi tu camión: {orig} a {dest}."

                st.markdown(f"""
                    <div class="card-container {'card-concretada' if conc else ''}">
                        <div style="flex-grow:1;">
                            <p class="status-{'conc' if conc else 'dispo'}">● {'CONCRETADO' if conc else 'DISPONIBLE'}</p>
                            <p class="route-text">📍 {str(orig).upper()} ➔ {str(dest).upper()}</p>
                            <p class="detail-text" style="color:black !important;">🚛 {equi}</p>
                        </div>
                        {'' if conc else f'<a href="{link}" target="_blank" class="btn-wa">WHATSAPP</a>'}
                    </div>
                """, unsafe_allow_html=True)
                if not conc:
                    if st.button("Marcar Concretado", key=mid):
                        st.session_state.concretados.add(mid); st.rerun()
        except:
            st.warning("Esperando datos...")
