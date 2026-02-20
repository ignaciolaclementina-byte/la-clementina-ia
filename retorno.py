import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

# --- 2. GESTIÓN DE ESTADO ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! -- Consultas aquí -- 🚛 Creado por Ignacio Diaz"

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 3. ESTILOS VIP ---
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

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- 4. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

def es_vip(dato):
    lista_vip = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista_vip

# Carga de datos
try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch_raw, df_ca_raw = pd.DataFrame(), pd.DataFrame()

# --- 5. RADAR ---
st.markdown(f"""<div class="radar-container"><marquee scrollamount="8">⭐ {st.session_state.anuncios} -- 🚛 Creado por Ignacio Diaz.</marquee></div>""", unsafe_allow_html=True)

# --- 6. BÚSQUEDA ---
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c4:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear(); st.rerun()

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# PESTAÑA: SOY EMPRESA
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
                st.success("Publicada!"); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['es_vip'] = df_ch_raw.iloc[:, 5].apply(es_vip)
            df_final_ch = df_ch_raw[df_ch_raw.iloc[:, 0].apply(es_hoy)].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ch.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ CHOFER VIP</div>' if r['es_vip'] else ""
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">💬 CONTACTAR</a></div>''', unsafe_allow_html=True)

# PESTAÑA: SOY CHOFER
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_camion", clear_on_submit=True):
            o = st.selectbox("Prov. Origen", PROVINCIAS[1:]); lo = st.text_input("Loc. Origen")
            d = st.selectbox("Prov. Destino", PROVINCIAS[1:]); ld = st.text_input("Loc. Destino")
            e = st.selectbox("Equipo", EQUIPOS[1:]); w = st.text_input("WhatsApp"); cu = st.text_input("CUIT")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cu, "entry.1574172378": w})
                st.success("Publicado!"); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['es_vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_final_ca = df_ca_raw[df_ca_raw.iloc[:, 0].apply(es_hoy)].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ca.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if r['es_vip'] else ""
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">💬 CONSULTAR</a></div>''', unsafe_allow_html=True)

# --- 7. PANEL DE CONTROL ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (ADMIN)"):
    st.session_state.anuncios = st.text_area("Radar publicitario:", st.session_state.anuncios)
    st.session_state.socios_activos = st.text_area("Lista VIP (separada por comas):", st.session_state.socios_activos)
    if st.button("🚀 ACTUALIZAR SISTEMA"): st.rerun()

# --- 8. PIE DE PÁGINA LEGAL BLINDADO ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p><b>AVISO LEGAL Y TÉRMINOS DE USO</b></p>
    <p style="max-width: 800px; margin: 0 auto; line-height: 1.6;">
        Queda terminantemente <b>prohibida la réplica, copia o distribución total o parcial</b> de esta interfaz, 
        código o marca sin autorización expresa de Ignacio Diaz. <br>
        El desarrollador <b>no se responsabiliza</b> por la veracidad de los datos cargados por los usuarios, 
        ni por los acuerdos, fletes o transacciones comerciales derivados del uso de esta plataforma. 
        El uso de esta herramienta es bajo absoluta responsabilidad de los usuarios.
    </p>
    <p style="margin-top: 20px; color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP - Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
