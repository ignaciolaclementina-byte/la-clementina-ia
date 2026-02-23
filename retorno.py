import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ Y SUS LEGALES) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()

if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. GESTIÓN DE ESTADO ---
if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "FLEMING, 20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! -- Consultas aquí --"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; }
    .card-white { background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6; border: 4px solid #f1c40f; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241,196,15,0.6); }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 65px; background-color: #2c3e50 !important; color: white !important; font-size: 18px; font-weight: 900; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- 5. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    if not dato or str(dato).lower() in ["-", "nan", ""]: return False
    lista_vip = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return any(vip in str(dato).upper() for vip in lista_vip)

# --- 6. DATOS ---
try:
    df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch, df_ca = pd.DataFrame(), pd.DataFrame()

# --- 7. BÚSQUEDA ---
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR"): st.cache_data.clear(); st.rerun()

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">🚛 FECHA: {b_fecha.strftime("%d/%m/%Y")} -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz y sus legales.</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# --- TAB 1: EMPRESA BUSCA CAMION ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_carga", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Carga"); en = st.text_input("Nombre Empresa")
            ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":f"{eo} ({elo})","entry.170847116":f"{ed} ({eld})","entry.576675281":ec,"entry.1930562861":en,"entry.466540450":ew})
                st.success("Publicado"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ch.empty:
            for _, r in df_ch.iterrows():
                try:
                    if pd.to_datetime(r[0], dayfirst=True).date() == b_fecha:
                        if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                            # En Camiones: WhatsApp es r[4] y CUIT es r[5]
                            es_v = es_vip(r[5]) if len(r)>5 else False
                            clase = "card-vip" if es_v else "card-white"
                            label = '<div class="vip-label">⭐ CHOFER VIP</div>' if es_v else ""
                            cuit_val = str(r[5]).replace(".0", "") if len(r)>5 else "-"
                            w = limpiar_wsp(r[4]) if len(r)>4 else "5491111111111"
                            msg = urllib.parse.quote(f"¡Hola! Te contacto a través de *RETORNO MATCH VIP* 🚛.\n\nHe visto tu camión *{r[3]}* disponible para la ruta:\n📍 *ORIGEN:* {r[1]}\n🏁 *DESTINO:* {r[2]}\n\n¿Sigue disponible para cargar?")
                            st.markdown(f'<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>ID/CUIT:</b> {cuit_val}<br><a href="https://api.whatsapp.com/send?phone={w}&text={msg}" target="_blank" class="btn-wsp">💬 CONTACTAR POR WHATSAPP</a></div>', unsafe_allow_html=True)
                except: continue

# --- TAB 2: CHOFER BUSCA CARGA ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_camion", clear_on_submit=True):
            o = st.selectbox("Origen", PROVINCIAS[1:]); lo = st.text_input("Loc. Origen")
            d = st.selectbox("Destino", PROVINCIAS[1:]); ld = st.text_input("Loc. Destino")
            e = st.selectbox("Equipo", EQUIPOS[1:]); cu = st.text_input("CUIT/ID")
            w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144":f"{o} ({lo})","entry.1519265625":f"{d} ({ld})","entry.597193898":e,"entry.1542650763":cu,"entry.1574172378":w})
                st.success("Publicado"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ca.empty:
            for _, r in df_ca.iterrows():
                try:
                    if pd.to_datetime(r[0], dayfirst=True).date() == b_fecha:
                        if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                            # En Cargas: WhatsApp es r[4] y Empresa es r[5]
                            es_v = es_vip(r[5]) if len(r)>5 else False
                            clase = "card-vip" if es_v else "card-white"
                            label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if es_v else ""
                            emp = str(r[5]).replace(".0", "") if len(r)>5 else "-"
                            w = limpiar_wsp(r[4]) if len(r)>4 else "5491111111111"
                            msg = urllib.parse.quote(f"¡Hola! Te hablo por la carga publicada en *RETORNO MATCH VIP* 🚛.\n\n📦 *DETALLE:* {r[3]}\n📍 *RUTA:* {r[1]} ➔ {r[2]}\n\n¿Sigue disponible?")
                            st.markdown(f'<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {emp}<br><a href="https://api.whatsapp.com/send?phone={w}&text={msg}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>', unsafe_allow_html=True)
                except: continue

# --- 8. PANEL DE CONTROL (BOTONES DE BORRADO) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (SÓLO IGNACIO DIAZ)"):
    if st.text_input("PIN Admin:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Radar publicitario:", st.session_state.anuncios)
        st.markdown("### ⭐ GESTIÓN DE SOCIOS VIP")
        lista_vips = [s.strip() for s in st.session_state.socios_activos.split(",") if s.strip()]
        for socio in lista_vips:
            cv1, cv2 = st.columns([4, 1])
            with cv1: st.code(socio)
            with cv2:
                if st.button("🗑️ Borrar", key=f"del_{socio}"):
                    lista_vips.remove(socio); st.session_state.socios_activos = ", ".join(lista_vips); st.rerun()
        nuevo_v = st.text_input("Agregar VIP:")
        if st.button("➕ AGREGAR"):
            if nuevo_v and nuevo_v not in lista_vips:
                lista_vips.append(nuevo_v); st.session_state.socios_activos = ", ".join(lista_vips); st.rerun()

# --- 9. PIE DE PÁGINA LEGAL ---
st.markdown(f'<div class="legal-footer"><p style="font-size:18px; font-weight:bold;">Creado por Ignacio Diaz y sus legales</p><p>© 2026 RETORNO MATCH VIP</p></div>', unsafe_allow_html=True)
