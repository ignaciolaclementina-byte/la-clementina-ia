import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 

# --- 2. SISTEMA ANTI-PAUSA (KEEP ALIVE NATIVO) ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()

if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. GESTIÓN DE DATOS Y VIP GLOBAL ---
@st.cache_data(ttl=15)
def cargar_datos_seguros():
    try:
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! -- Consultas aquí --"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP (DISEÑO BLINDADO) ---
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
        margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center;
    }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333;
    }
    .card-vip {
        background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.5);
    }
    .vip-label {
        background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; 
        font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px;
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 70px !important; background-color: #2c3e50 !important; color: white !important; font-size: 18px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .legal-footer { 
        text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; 
        font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES ---
def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_fecha_seleccionada(f, fecha_target):
    try:
        return pd.to_datetime(f, dayfirst=True).date() == fecha_target
    except: return False

def es_vip(dato):
    dato_str = str(dato).strip().upper().replace(".0", "")
    return dato_str in LISTA_VIPS_GLOBAL

# --- 6. BÚSQUEDA ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# --- 7. RADAR ---
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">🚛 FECHA: {b_fecha.strftime("%d/%m/%Y")} -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz.</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# --- TAB: CAMIONES (ESTRUCTURA 1, 2.2) ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_carga", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Carga"); en = st.text_input("Nombre Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['es_vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_final_ch = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ch.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                    # SOLUCIÓN CUIT: Columna 4 para CUIT, Columna 5 para WhatsApp
                    cuit_final = limpiar_dato_numerico(r[4])
                    whatsapp_valor = limpiar_wsp(r[5])
                    
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ CHOFER VIP</div>' if r['es_vip'] else ""
                    st.markdown(f'''
                    <div class="{clase}">{label}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit_final}<br>
                        <a href="https://api.whatsapp.com/send?phone={whatsapp_valor}&text=Hola!" target="_blank" class="btn-wsp">💬 CONTACTAR POR WHATSAPP</a>
                    </div>''', unsafe_allow_html=True)

# --- TAB: CARGAS (ESTRUCTURA 1, 2.2) ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_camion", clear_on_submit=True):
            o = st.selectbox("Origen", PROVINCIAS[1:]); d = st.selectbox("Destino", PROVINCIAS[1:])
            e = st.selectbox("Equipo", EQUIPOS[1:]); cu = st.text_input("CUIT/ID"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1542650763": cu, "entry.1574172378": w})
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['es_vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_final_ca = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ca.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if r['es_vip'] else ""
                    st.markdown(f'<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=Hola!" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>', unsafe_allow_html=True)

# --- 8. PANEL DE CONTROL ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (SÓLO IGNACIO DIAZ)"):
    if st.text_input("Introduce PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Editar Radar:", st.session_state.anuncios)
        url_vip_directo = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}"
        st.markdown(f'<a href="{url_vip_directo}" target="_blank" style="background:#f1c40f; color:black; padding:15px; border-radius:10px; font-weight:bold; text-decoration:none; display:block; text-align:center;">➕ CARGAR VIP AL SISTEMA GLOBAL (EXCEL)</a>', unsafe_allow_html=True)
        if st.button("🚀 ACTUALIZAR TODO"): st.cache_data.clear(); st.rerun()

# --- 9. PIE DE PÁGINA LEGAL ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="font-style: italic;">No nos responsabilizamos por acuerdos entre partes. La plataforma es nexo informativo.</p>
    <p><b>Prohibida la copia total o parcial sin autorización de Ignacio Diaz.</b></p>
    <p>© 2026 RETORNO MATCH VIP - Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
