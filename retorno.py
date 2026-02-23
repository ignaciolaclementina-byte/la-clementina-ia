import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚚", layout="wide")

# --- 2. CONSTANTES Y ESTRUCTURA (CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

# --- 3. ESTILOS CSS (MEJORA VISUAL Y BOTÓN COMPARTIR) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 2px solid #f1c40f; text-align: center; }
    
    /* Cards Premium con bordes mejorados */
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid #ddd; border-left: 10px solid #3498db; color: #333; position: relative; }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.4); border-left: 10px solid #f1c40f; position: relative; }
    
    /* Badge NUEVO */
    .badge-nuevo { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; position: absolute; top: 10px; right: 10px; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }

    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    
    /* Botón flotante Compartir */
    .share-btn { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-decoration: none; font-size: 30px; }
</style>
<a href="https://api.whatsapp.com/send?text=¡Mirá esta App de Retornos! 🚚 https://retornomatchvip.streamlit.app" class="share-btn" target="_blank">📲</a>
""", unsafe_allow_html=True)

# --- 4. FUNCIONES DE LÓGICA ---
def sanitizar(dato):
    if pd.isna(dato): return ""
    return "".join(filter(str.isdigit, str(dato).replace(".0", "")))

def limpiar_wsp(num):
    clean = sanitizar(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

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

def es_nuevo(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True)
        return (datetime.now() - ts) < timedelta(hours=2)
    except: return False

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True).date() == target
    except: return False

# --- 5. CARGA INICIAL ---
if "anuncios" not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al sistema!"

with st.spinner("🚀 Sincronizando con base de datos VIP..."):
    df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

hoy = datetime.now().date()

# --- 6. INTERFAZ DE FILTROS ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)

b_q = st.text_input("📍 BUSCADOR RÁPIDO (Localidad, Empresa o Carga)", placeholder="Ej: San Jorge, Rosario, Soja...").upper()

# Conteos Radar
cant_ch = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_ca = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

radar_txt = f"🔥 VIVO: {cant_ch} Camiones y {cant_ca} Cargas -- ⭐ {st.session_state.anuncios} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES", "🏢 VER CARGAS"])

# --- TAB 1: CAMIONES ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa")
            ew = st.text_input("WhatsApp", help="Ej: 1123456789 (Sin 0 ni 15)")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": sanitizar(ew)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: str(r[4]).strip().upper() in LISTA_VIPS_GLOBAL or str(r[5]).strip().upper() in LISTA_VIPS_GLOBAL, axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f.iterrows():
                # Filtro de búsqueda libre
                contenido = f"{r[1]} {r[2]} {r[3]} {r[4]} {r[5]}".upper()
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and \
                   (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and \
                   (b_e=="CUALQUIERA" or b_e==str(r[3])) and \
                   (b_q in contenido):
                    
                    cuit = sanitizar(r[4]) if len(sanitizar(r[4])) == 11 else sanitizar(r[5])
                    wsp = sanitizar(r[5]) if cuit == sanitizar(r[4]) else sanitizar(r[4])
                    badge = '<div class="badge-nuevo">NUEVO</div>' if es_nuevo(r[0]) else ''
                    
                    msg = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n✅ *INTERÉS EN UNIDAD*\n📍 RUTA: {r[1]} -> {r[2]}\n🚛 EQUIPO: {r[3]}\n\n¿Está disponible?")
                    
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {badge}
                        {"<div class='vip-label'>⭐ CHOFER VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>EQUIPO:</b> {r[3]} | 🆔 <b>ID:</b> {cuit}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text={msg}" target="_blank" class="btn-wsp">✉️ CONTACTAR AHORA</a>
                    </div>''', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            o_p = st.selectbox("Prov. Origen", PROVINCIAS[1:]); o_l = st.text_input("Loc. Origen")
            d_p = st.selectbox("Prov. Destino", PROVINCIAS[1:]); d_l = st.text_input("Loc. Destino")
            e_t = st.selectbox("Equipo", EQUIPOS[1:]); c_i = st.text_input("CUIT/ID"); w_n = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o_p} ({o_l})", "entry.1519265625": f"{d_p} ({d_l})", "entry.597193898": e_t, "entry.1542650763": sanitizar(c_i), "entry.1574172378": sanitizar(w_n)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(lambda x: str(x).strip().upper() in LISTA_VIPS_GLOBAL)
            df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f2.iterrows():
                contenido_ca = f"{r[1]} {r[2]} {r[3]} {r[5]}".upper()
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and \
                   (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and \
                   (b_q in contenido_ca):
                    
                    badge_ca = '<div class="badge-nuevo">NUEVO</div>' if es_nuevo(r[0]) else ''
                    msg_ca = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n📦 *CONSULTA POR CARGA*\n🏢 EMPRESA: {r[5]}\n📍 RUTA: {r[1]} -> {r[2]}\n\n¿Sigue disponible?")
                    
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {badge_ca}
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_ca}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a>
                    </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div style="text-align: center; color: white; padding: 50px 20px; opacity: 0.8; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px;">
    <p style="font-size: 18px; font-weight: bold;">Creado por Ignacio Diaz</p>
    <p>© 2026 RETORNO MATCH VIP - Prohibida la copia total o parcial.</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Mensaje Radar:", st.session_state.anuncios)
        st.markdown(f'<a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}" target="_blank">➕ GESTIONAR LISTA VIP</a>', unsafe_allow_html=True)
