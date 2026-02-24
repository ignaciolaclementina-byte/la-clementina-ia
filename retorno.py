import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import re

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=10)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# Lógica de tiempo robusta
hoy = datetime.now().date()
def es_fecha(f, target):
    try: 
        return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: 
        return False

cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS VIP PERSONALIZADOS (ESTRUCTURA IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6 !important; border: 3px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.5); }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #1b5e20; }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px 20px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 60px !important; background-color: #2c3e50 !important; color: white !important; font-size: 16px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES AUXILIARES ---
def limpiar_dato_numerico(dato):
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = limpiar_dato_numerico(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True): 
        st.cache_data.clear(); st.rerun()

radar_txt = f"🌾 COSECHA ACTIVA: {cant_camiones} Camiones y {cant_cargas} Cargas -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES DISPONIBLES", "🏢 CARGAS DISPONIBLES", "🌾 ARRIME COSECHA"])

# --- TAB 1: CAMIONES ---
with tab1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar mi Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Nombre Empresa"); ew = st.text_input("WhatsApp de Contacto")
            if st.form_submit_button("SUBIR CARGA AL SISTEMA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.success("¡Carga Publicada!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                    val_a, val_b = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                    cuit, wsp = (val_a, val_b) if len(val_a) == 11 else (val_b, val_a)
                    texto_wsp = f"─── *RETORNO MATCH VIP* ───\n✅ *SOLICITUD DE TRANSPORTE*\n\nEstimado, me interesa su unidad {r[3]} en {r[1]} para realizar un viaje. ¿Está disponible? Saludos."
                    link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text={urllib.parse.quote(texto_wsp)}"
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}">{"<div class=\'vip-label\'>⭐ CHOFER VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {cuit}<br><a href="{link_wsp}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA FORMAL</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar mi Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            o_prov = st.selectbox("Prov. Origen", PROVINCIAS[1:]); o_loc = st.text_input("Loc. Origen")
            d_prov = st.selectbox("Prov. Destino", PROVINCIAS[1:]); d_loc = st.text_input("Loc. Destino")
            e_tipo = st.selectbox("Equipo", EQUIPOS[1:]); cu_id = st.text_input("CUIT/ID"); wsp_num = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN AL SISTEMA"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o_prov} ({o_loc})", "entry.1519265625": f"{d_prov} ({d_loc})", "entry.597193898": e_tipo, "entry.1542650763": cu_id, "entry.1574172378": wsp_num})
                st.cache_data.clear(); st.success("¡Camión Publicado!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_ca_filtered = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            df_f2 = df_ca_filtered[df_ca_filtered.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f2.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    texto_wsp_ca = f"─── *RETORNO MATCH VIP* ───\n📦 *INTERÉS EN CARGA*\n\nHola, consulto por la carga {r[3]} de {r[1]} a {r[2]} vista en el sistema. ¿Sigue disponible? Gracias."
                    link_wsp_ca = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(texto_wsp_ca)}"
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}">{"<div class=\'vip-label\'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br><a href="{link_wsp_ca}" target="_blank" class="btn-wsp">📩 CONSULTAR DISPONIBILIDAD</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME COSECHA ---
with tab3:
    st.markdown("<h3 style='color:#f1c40f; text-align:center;'>🌾 SECCIÓN ESPECIAL: ARRIME DE COSECHA</h3>", unsafe_allow_html=True)
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        st.markdown("<h4 style='color:white;'>🚜 Nuevo Operativo</h4>", unsafe_allow_html=True)
        with st.form("f_arr", clear_on_submit=True):
            z_loc = st.text_input("📍 Zona/Localidad")
            g_det = st.text_input("🌾 Detalle (Grano/Trayecto)")
            t_val = st.text_input("💰 Tarifa")
            w_arr = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR ARRIME"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z_loc, "entry.576675281": f"ARRIME|{g_det}|{t_val}", "entry.1930562861": "COSECHA", "entry.466540450": w_arr})
                st.cache_data.clear(); st.success("¡Arrime Publicado!"); time.sleep(1); st.rerun()
    with col_a2:
        if not df_ca_raw.empty:
            df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for _, r in df_arrime.iterrows():
                texto_celda = str(r[3])
                if "|" in texto_celda:
                    parts = texto_celda.split("|")
                    detalle = parts[1] if len(parts) > 1 else texto_celda
                    tarifa = parts[2] if len(parts) > 2 else "A consultar"
                else:
                    detalle = texto_celda
                    numeros = re.findall(r'\d+', texto_celda)
                    tarifa = numeros[0] if numeros else "A consultar"

                msg_arr = f"─── *RETORNO MATCH VIP - ARRIME* ───\n🌾 *COSECHA*\n\nHola, me interesa el arrime en {r[2]}. ¿Cómo procedemos?"
                link_arr = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(msg_arr)}"
                st.markdown(f'''
                <div class="card-cosecha">
                    <div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>
                    <div style="margin: 10px 0;">
                        <b>🌾 DETALLE:</b> {detalle}<br>
                        <b>💰 TARIFA:</b> <span style="font-size:1.2em; font-weight:bold;">{tarifa}</span>
                    </div>
                    <a href="{link_arr}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">🚜 CONTACTAR POR ARRIME</a>
                </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white; margin-bottom: 5px;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p style="font-style: italic;">No nos responsabilizamos por acuerdos entre partes.</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Texto Radar:", st.session_state.anuncios)
