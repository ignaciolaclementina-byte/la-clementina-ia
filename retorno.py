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

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()

if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. GESTIÓN DE ESTADO ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡SISTEMA VIP ACTIVADO! -- Consultas aquí --"

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP (BLINDADOS) ---
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
    .card-vip {
        background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.5);
    }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333;
    }
    .vip-label {
        background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; 
        font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px;
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { 
        text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; 
        font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# --- 5. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
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
    lista_vip = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista_vip

# --- 6. FILTROS ---
c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# Carga de datos
try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
    cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))])
except:
    df_ch_raw, df_ca_raw = pd.DataFrame(), pd.DataFrame()
    cant_camiones = 0

# --- 7. RADAR ---
st.markdown(f"""
<div class="radar-container">
    <marquee scrollamount="8">
        🚛 FECHA: {b_fecha.strftime('%d/%m/%Y')} -- ACTIVOS: {cant_camiones} CAMIONES -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz y sus legales.
    </marquee>
</div>
""", unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# PESTAÑA: SOY EMPRESA (VER CAMIONES)
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_carga", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Carga"); en = st.text_input("Nombre Empresa")
            ew = st.text_input("WhatsApp (Sin 0 ni 15)", placeholder="Ej: 1122334455")
            if st.form_submit_button("SUBIR CARGA"):
                data_carga = {"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew}
                requests.post(URL_CARGAS_POST, data=data_carga)
                st.success("¡Carga Publicada!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            # CORRECCIÓN FINAL DE COLUMNAS PARA CHOFERES:
            # Si r[4] muestra el WhatsApp (3406649346) y r[5] el CUIT (20367111128):
            # Cambiamos VIP para que valide contra r[5] (el CUIT real)
            df_ch_raw['es_vip'] = df_ch_raw.iloc[:, 5].apply(es_vip) 
            df_final_ch = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            
            for _, r in df_final_ch.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ CHOFER VIP</div>' if r['es_vip'] else ""
                    
                    # --- FORZADO DE DATOS CORRECTOS ---
                    cuit_real = str(r[5]).replace(".0", "") # Tomamos la col 5 para el CUIT
                    wsp_real = str(r[4])                    # Tomamos la col 4 para el WHATSAPP
                    
                    msg = urllib.parse.quote(f"Hola! Te contacto desde *RETORNO MATCH VIP* 🚛. Vi tu camión *{r[3]}* disponible para la ruta *{r[1]} -> {r[2]}*. ¿Sigue disponible?")
                    
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit_real}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp_real)}&text={msg}" target="_blank" class="btn-wsp">💬 CONTACTAR POR WHATSAPP</a></div>''', unsafe_allow_html=True)

# PESTAÑA: SOY CHOFER (VER CARGAS)
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_camion", clear_on_submit=True):
            o = st.selectbox("Prov. Origen", PROVINCIAS[1:]); lo = st.text_input("Loc. Origen")
            d = st.selectbox("Prov. Destino", PROVINCIAS[1:]); ld = st.text_input("Loc. Destino")
            e = st.selectbox("Equipo", EQUIPOS[1:]); cu = st.text_input("CUIL/CUIT", placeholder="Ej: 20334445551")
            w = st.text_input("WhatsApp (Sin 0 ni 15)", placeholder="Ej: 1122334455")
            if st.form_submit_button("SUBIR CAMIÓN"):
                data_camion = {"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cu, "entry.1574172378": w}
                requests.post(URL_CHOFERES_POST, data=data_camion)
                st.success("¡Camión Publicado!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['es_vip'] = df_ca_raw.iloc[:, 4].apply(es_vip) 
            df_final_ca = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha_seleccionada(x, b_fecha))].sort_values(by='es_vip', ascending=False)
            for _, r in df_final_ca.iterrows():
                if (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    clase = "card-vip" if r['es_vip'] else "card-white"
                    label = '<div class="vip-label">⭐ EMPRESA VIP</div>' if r['es_vip'] else ""
                    
                    empresa_nombre = str(r[4]).replace(".0", "")
                    wsp_carga = str(r[5])
                    msg_carga = urllib.parse.quote(f"Hola! Vi tu carga de *{r[1]}* a *{r[2]}* en *RETORNO MATCH VIP*. ¿Sigue disponible?")
                    
                    st.markdown(f'''<div class="{clase}">{label}<div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {empresa_nombre}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp_carga)}&text={msg_carga}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a></div>''', unsafe_allow_html=True)

# --- 8. PIE DE PÁGINA LEGAL ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz y sus legales</p>
    <p style="font-style: italic;">No me responsabilizo por los acuerdos, cargas o transacciones realizadas entre las partes. La plataforma actúa únicamente como nexo informativo.</p>
    <p><b>Queda terminantemente prohibida la réplica, copia o distribución total o parcial de este sistema sin autorización expresa.</b></p>
    <p>© 2026 RETORNO MATCH VIP - Todos los derechos reservados.</p>
</div>
""", unsafe_allow_html=True)
