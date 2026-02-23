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

# --- LLAVE DE ACCESO ADMIN ---
ADMIN_PIN = "1323" 

# --- 2. SISTEMA ANTI-PAUSA (KEEP ALIVE NATIVO) ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()

if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. GESTIÓN DE ESTADO PERMANENTE ---
# Ignacio: Agregá aquí los nombres o CUITs que quieras que TODOS vean como VIP siempre.
if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "FLEMING, 20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! -- Consultas aquí --"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP (DISEÑO BLINDADO Y RESPONSIVO) ---
st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .radar-container {
        background: rgba(231, 76, 60, 0.9);
        color: white; padding: 10px; border-radius: 10px;
        margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f;
    }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333;
    }
    .card-vip {
        background: #fff9e6 !important; border: 4px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        color: #333; box-shadow: 0px 4px 25px rgba(241, 196, 15, 0.8);
    }
    .vip-label {
        background: #f1c40f; color: black; padding: 6px 14px; border-radius: 20px; 
        font-weight: 900; font-size: 15px; display: inline-block; margin-bottom: 10px;
        border: 1px solid black;
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 60px !important; background-color: #2c3e50 !important; color: white !important; font-size: 16px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .legal-footer { 
        text-align: center; color: rgba(255,255,255,0.7); padding: 40px 20px; 
        font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- 5. FUNCIONES ---
def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    clean = "".join(filter(str.isdigit, s))
    return clean

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_fecha_seleccionada(f, fecha_target):
    try:
        fecha_planilla = pd.to_datetime(f, dayfirst=True).date()
        return fecha_planilla == fecha_target
    except:
        return False

def es_vip(dato):
    # Detección inteligente: Si el dato está en la lista VIP o la lista VIP contiene el dato
    lista_vip = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    dato_str = str(dato).strip().upper()
    if dato_str.endswith(".0"): dato_str = dato_str[:-2]
    
    for vip in lista_vip:
        if vip in dato_str or dato_str in vip:
            return True
    return False

# --- 6. BÚSQUEDA ---
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear(); st.rerun()

try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
    cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))])
except:
    df_ch_raw, df_ca_raw = pd.DataFrame(), pd.DataFrame()
    cant_camiones = 0

# --- 7. RADAR AUTOMATIZADO ---
st.markdown(f"""
<div class="radar-container">
    <marquee scrollamount="8">
        🚛 FECHA: {b_fecha.strftime('%d/%m/%Y')} -- ACTIVOS: {cant_camiones} CAMIONES -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz y sus legales.
    </marquee>
</div>
""", unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# --- TAB 1: EMPRESAS BUSCANDO (Móvil First) ---
with t1:
    col_res1, col_form1 = st.columns([2.2, 1])
    with col_res1:
        st.markdown("<h4 style='color:white;'>📋 Camiones para hoy</h4>", unsafe_allow_html=True)
        if not df_ch_raw.empty:
            df_ch_raw['es_vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_final_ch = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ch.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ CHOFER VIP</div>' if r['es_vip'] else ""
                    v4, v5 = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                    cuit_final = v5 if len(v5) == 11 else v4
                    wsp_final = v4 if cuit_final == v5 else v5
                    msg = urllib.parse.quote(f"¡Hola! Te contacto a través de *RETORNO MATCH VIP* 🚛.\n\nHe visto tu camión *{r[3]}* disponible para la ruta:\n📍 *ORIGEN:* {r[1]}\n🏁 *DESTINO:* {r[2]}\n\n¿Sigue disponible para cargar? ¡Espero tu respuesta!")
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit_final}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp_final)}&text={msg}" target="_blank" class="btn-wsp">💬 CONTACTAR POR WHATSAPP</a></div>''', unsafe_allow_html=True)

# --- TAB 2: CHOFERES BUSCANDO (Móvil First) ---
with t2:
    col_res2, col_form2 = st.columns([2.2, 1])
    with col_res2:
        st.markdown("<h4 style='color:white;'>📢 Cargas para hoy</h4>", unsafe_allow_html=True)
        if not df_ca_raw.empty:
            # Aquí aplicamos el filtro VIP a la columna de empresa (índice 5)
            df_ca_raw['es_vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_final_ca = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ca.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if r['es_vip'] else ""
                    empresa_visual = str(r[5]).replace(".0", "").strip()
                    msg_carga = urllib.parse.quote(f"¡Hola! Te hablo por la carga publicada en *RETORNO MATCH VIP* 🚛.\n\n📦 *DETALLE:* {r[3]}\n📍 *RUTA:* {r[1]} ➔ {r[2]}\n🏢 *EMPRESA:* {empresa_visual}\n\n¿Sigue disponible? Me interesa consultar más detalles. ¡Gracias!")
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {empresa_visual}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_carga}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>''', unsafe_allow_html=True)

# --- 8. PANEL DE CONTROL (BLINDADO) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (SÓLO IGNACIO DIAZ)"):
    input_pin = st.text_input("PIN Admin:", type="password")
    if input_pin == ADMIN_PIN:
        st.success("Acceso Concedido, Ignacio.")
        st.session_state.anuncios = st.text_area("Radar publicitario:", st.session_state.anuncios)
        st.info("Nota: Los VIP agregados aquí solo duran esta sesión. Para hacerlos permanentes, dejalos escritos arriba en el código.")
        nuevo_vip = st.text_input("Agregar CUIT/Nombre VIP temporal:")
        if st.button("ACTUALIZAR"):
            st.session_state.socios_activos += f", {nuevo_vip}"
            st.rerun()
    elif input_pin != "":
        st.error("PIN Incorrecto.")

# --- 9. PIE DE PÁGINA LEGAL (BLINDADO) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz y sus legales</p>
    <p style="font-style: italic;">No nos responsabilizamos por acuerdos entre partes. La plataforma es un nexo informativo.</p>
    <p><b>Prohibida la copia total o parcial sin autorización expresa de Ignacio Diaz.</b></p>
    <p>© 2026 RETORNO MATCH VIP - Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
