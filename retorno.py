import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

# Lista Maestra de Provincias para Blindar Búsqueda
PROVINCIAS = [
    "CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", 
    "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", 
    "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", 
    "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"
]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS Y DISEÑO (BLINDADO) ---
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; margin: 5px; border: 1px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .footer { text-align: center; color: white; opacity: 0.9; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .legal { font-size: 10px; color: #bdc3c7; margin-top: 10px; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- FUNCIONES ---
def enviar_a_google(url, data):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try: return requests.post(url, data=data, headers=headers).status_code == 200
    except: return False

def es_de_hoy(fecha_str):
    try:
        fecha_dt = pd.to_datetime(fecha_str).date()
        return fecha_dt == datetime.now().date()
    except: return False

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    if not clean.startswith("549"): clean = "549" + clean
    return clean

# --- BÚSQUEDA ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c_b2: b_destino = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- PESTAÑA 1: CHOFER ---
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("<h3 style='color:white;'>📢 Publicar Camión</h3>", unsafe_allow_html=True)
        with st.form("form_ch", clear_on_submit=True):
            o = st.selectbox("📍 Provincia Origen", PROVINCIAS[1:])
            loc_o = st.text_input("Localidad Origen")
            d = st.selectbox("🏁 Provincia Destino", PROVINCIAS[1:])
            loc_d = st.text_input("Localidad Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp"); cuit = st.text_input("🆔 CUIT")
            ld = st.text_input("📂 Link Documentación")
            
            if st.form_submit_button("PUBLICAR"):
                cuit_c = "".join(filter(str.isdigit, cuit))
                if len(cuit_c) != 11: st.error("❌ CUIT inválido")
                else:
                    payload = {"entry.1304806144": f"{o} ({loc_o})", "entry.1519265625": f"{d} ({loc_d})", "entry.597193898": e, "entry.1542650763": cuit_c, "entry.769375120": ld, "entry.1574172378": w}
                    if enviar_a_google(URL_CHOFERES_POST, payload):
                        st.success("✅ Publicado"); time.sleep(1); st.rerun()

    with col_d:
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            count_c = 0
            for _, r in df_c.iloc[::-1].iterrows():
                if es_de_hoy(r[0]): 
                    # Filtro inteligente: Si es "CUALQUIERA" muestra todo, sino filtra por provincia
                    if (b_origen == "CUALQUIERA" or b_origen in str(r[1]).upper()) and (b_destino == "CUALQUIERA" or b_destino in str(r[2]).upper()):
                        num_f = limpiar_wsp(r[4])
                        msg = urllib.parse.quote(f"Hola! Vi tu carga en *RETORNO MATCH*:\n📍 Origen: {r[1]}\n🏁 Destino: {r[2]}\n📦 Carga: {r[3]}\n¿Sigue disponible?")
                        st.markdown(f'<div class="card-white"><div class="route-txt">📍 {r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br><b>⏳ SALE:</b> {r[6]}<a href="https://api.whatsapp.com/send?phone={num_f}&text={msg}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>', unsafe_allow_html=True)
                        count_c += 1
            if count_c == 0: st.info("No hay cargas para esta ruta hoy.")
        except: st.info("Actualizando...")

# --- PESTAÑA 2: EMPRESA ---
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("<h3 style='color:white;'>🏢 Publicar Carga</h3>", unsafe_allow_html=True)
        with st.form("form_em", clear_on_submit=True):
            eo = st.selectbox("📍 Provincia Origen", PROVINCIAS[1:])
            loc_eo = st.text_input("Localidad Origen")
            ed = st.selectbox("🏁 Provincia Destino", PROVINCIAS[1:])
            loc_ed = st.text_input("Localidad Destino")
            ec = st.text_input("📦 Carga"); en = st.text_input("Empresa")
            ef = st.text_input("⏳ Cuándo"); ew = st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                payload = {"entry.610070407": f"{eo} ({loc_eo})", "entry.170847116": f"{ed} ({loc_ed})", "entry.576675281": ec, "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew}
                if enviar_a_google(URL_CARGAS_POST, payload):
                    st.success("✅ Carga subida"); time.sleep(1); st.rerun()

    with col_b:
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("-")
            count_h = 0
            for _, r in df_h.iloc[::-1].iterrows():
                if es_de_hoy(r[0]):
                    if (b_origen == "CUALQUIERA" or b_origen in str(r[1]).upper()) and (b_destino == "CUALQUIERA" or b_destino in str(r[2]).upper()):
                        num_h = limpiar_wsp(r[4])
                        msg_h = urllib.parse.quote(f"Hola! Vi tu camión en *RETORNO MATCH*:\n🚛 Equipo: {r[3]}\n📍 Ubicación: {r[1]}\n🏁 Destino: {r[2]}\n¿Estás disponible?")
                        st.markdown(f'<div class="card-white"><div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div><b>⚙️ EQUIPO:</b> {r[3]}<br><b>🆔 CUIT:</b> {r[5]}<div style="display:flex;gap:10px;"><a href="https://api.whatsapp.com/send?phone={num_h}&text={msg_h}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONTACTAR</a><a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 PAPELES</a></div></div>', unsafe_allow_html=True)
                        count_h += 1
            if count_h == 0: st.info("No hay camiones en esta ruta hoy.")
        except: st.info("Actualizando...")

# --- FOOTER BLINDADO ---
st.markdown(f"""
    <div class="footer">
        <p><b>© 2026 RETORNO MATCH - San Jorge, Santa Fe</b></p>
        <p>Creado por <b>Ignacio Diaz y sus legales</b></p>
        <div class="legal">
            <b>AVISO LEGAL:</b> Queda estrictamente prohibida la reproducción total o parcial de esta estructura e interfaz bajo apercibimiento de ley. 
            RETORNO MATCH actúa como nexo informativo.
        </div>
    </div>
    """, unsafe_allow_html=True)
