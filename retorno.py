import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS ORIGINALES BLINDADOS ---
st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; position: relative; }
    .card-urgent { background: #fff5f5 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #e74c3c; color: #333; position: relative; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .badge-dist { background: #f1c40f; color: #2c3e50; padding: 2px 6px; border-radius: 4px; font-size: 13px; font-weight: bold; margin-left: 10px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .footer { text-align: center; color: white; padding: 40px; font-size: 14px; border-top: 0.5px solid rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE KM POR COORDENADAS (GRATUITO) ---
@st.cache_data
def get_coords(city):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(city + ', Argentina')}&format=json&limit=1"
        response = requests.get(url, headers={'User-Agent': 'RetornoMatchApp'}).json()
        if response:
            return float(response[0]['lat']), float(response[0]['lon'])
    except: return None
    return None

def calc_distancia(lat1, lon1, lat2, lon2):
    R = 6371 # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return int(R * c * 1.2) # Factor 1.2 para aproximar de "línea recta" a "ruta"

# --- 4. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c4:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_chofer", clear_on_submit=True):
            o = st.selectbox("Provincia Origen", PROVINCIAS[1:]); lo = st.text_input("Localidad")
            d = st.selectbox("Provincia Destino", PROVINCIAS[1:]); ld = st.text_input("Localidad")
            e = st.selectbox("Equipo", EQUIPOS[1:]); w = st.text_input("WhatsApp")
            cu = st.text_input("CUIT"); doc = st.text_input("Link Papeles")
            if st.form_submit_button("PUBLICAR"):
                data = {"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cu, "entry.769375120": doc, "entry.1574172378": w}
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        try:
            df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
            for _, r in df_ca.iloc[::-1].iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    urg = "🔥" in str(r[3])
                    # Cálculo de KM dinámico
                    c1 = get_coords(str(r[1]))
                    c2 = get_coords(str(r[2]))
                    dist_txt = ""
                    if c1 and c2:
                        km = calc_distancia(c1[0], c1[1], c2[0], c2[1])
                        dist_txt = f'<span class="badge-dist">~{km} KM</span>'
                    
                    st.markdown(f'''<div class="{"card-urgent" if urg else "card-white"}">
                        <div class="route-txt">{r[1]} ➔ {r[2]} {dist_txt}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}
                        <a href="https://api.whatsapp.com/send?phone={549}{r[4]}&text=Hola!" target="_blank" class="btn-wsp">💬 CONSULTAR</a>
                    </div>''', unsafe_allow_html=True)
        except: st.info("Cargando...")

# --- FOOTER (BLINDADO) ---
st.markdown(f"""<div class="footer"><p><b>© 2026 RETORNO MATCH - San Jorge, Santa Fe</b></p><p>Creado por <b>Ignacio Diaz y sus legales</b></p></div>""", unsafe_allow_html=True)
