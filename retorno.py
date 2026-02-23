import streamlit as st

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTRICTAMENTE EL PRIMER COMANDO) ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚚", layout="wide")

import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 2. CONFIGURACIÓN Y ESTRUCTURA (CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

# URLs de envío (Google Forms)
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323"
PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

# --- 3. FUNCIONES DE BLINDAJE (ANTI-ERRORES) ---

def safe_get(df_row, idx):
    """Obtiene un valor de la fila de forma segura."""
    try:
        val = df_row[idx]
        if pd.isna(val) or val == "nan": return ""
        return str(val).replace(".0", "").strip()
    except:
        return ""

def sanitizar(dato):
    """Limpia números (CUIT/Teléfono)."""
    s = safe_get([dato], 0)
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    """Prepara número para WhatsApp."""
    clean = sanitizar(num)
    if not clean or len(clean) < 7: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_nuevo(ts_str):
    """Detecta si el registro es de hace menos de 2 horas."""
    try:
        ts = pd.to_datetime(ts_str, dayfirst=True)
        return (datetime.now() - ts) < timedelta(hours=2)
    except: return False

def es_fecha_hoy(ts_str, target_date):
    """Compara fechas de forma ultra-segura."""
    try:
        return pd.to_datetime(ts_str, dayfirst=True).date() == target_date
    except: return False

@st.cache_data(ttl=15)
def cargar_todo():
    """Carga y pre-procesa todo como texto para evitar fallos de tipo."""
    try:
        t = int(time.time())
        # Carga forzando a que todo sea string (dtype=str)
        ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}", dtype=str).fillna("")
        ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}", dtype=str).fillna("")
        v_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", dtype=str).fillna("")
        vips = [str(x).upper().strip() for x in v_raw[0].tolist() if x]
        return ch, ca, vips
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), []

# --- 4. ESTILOS VISUALES ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 2px solid #f1c40f; text-align: center; }
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; position: relative; }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.4); border-left: 10px solid #f1c40f; position: relative; }
    .badge-nuevo { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; position: absolute; top: 10px; right: 10px; animation: flash 1.5s infinite; }
    @keyframes flash { 0% {opacity: 1;} 50% {opacity: 0.4;} 100% {opacity: 1;} }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .share-btn { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; width: 60px; height: 60px; border-radius: 50%; display: flex; align-items: center; justify-content: center; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-decoration: none; font-size: 30px; }
</style>
<a href="https://api.whatsapp.com/send?text=¡Mirá esta App de Retornos! 🚚 https://retorno-match-sanjorge.streamlit.app" class="share-btn" target="_blank">📲</a>
""", unsafe_allow_html=True)

# --- 5. CARGA DE DATOS ---
with st.spinner("Sincronizando con Ignacio Diaz..."):
    df_ch, df_ca, LISTA_VIPS = cargar_todo()

if 'anuncio' not in st.session_state: st.session_state.anuncio = "¡Bienvenido!"
hoy = datetime.now().date()

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: b_f = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)

b_q = st.text_input("📍 BUSCADOR RÁPIDO (Ciudad, Carga, Empresa...)", placeholder="Escribe aquí...").upper()

# Radar
ch_h = len(df_ch[df_ch.iloc[:,0].apply(lambda x: es_fecha_hoy(x, hoy))]) if not df_ch.empty else 0
ca_h = len(df_ca[df_ca.iloc[:,0].apply(lambda x: es_fecha_hoy(x, hoy))]) if not df_ca.empty else 0
radar_txt = f"🔥 HOY: {ch_h} Camiones y {ca_h} Cargas -- ⭐ {st.session_state.anuncio} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 VER CAMIONES", "🏢 VER CARGAS"])

# --- TAB CAMIONES ---
with tab1:
    f_izq, f_der = st.columns([1, 2.2])
    with f_izq:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_ca", clear_on_submit=True):
            o = st.selectbox("Origen", PROVINCIAS[1:]); lo = st.text_input("Loc. Origen")
            d = st.selectbox("Destino", PROVINCIAS[1:]); ld = st.text_input("Loc. Destino")
            c = st.text_input("Carga"); n = st.text_input("Empresa"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{o} ({lo})", "entry.170847116": f"{d} ({ld})", "entry.576675281": c, "entry.1930562861": n, "entry.466540450": sanitizar(w)})
                st.cache_data.clear(); st.success("¡Listado!"); time.sleep(1); st.rerun()
    with f_der:
        if not df_ch.empty:
            # Marcamos VIP
            df_ch['vip'] = df_ch.apply(lambda r: safe_get(r, 4).upper() in LISTA_VIPS or safe_get(r, 5).upper() in LISTA_VIPS, axis=1)
            # Filtramos
            mask = df_ch.iloc[:,0].apply(lambda x: es_fecha_hoy(x, b_f))
            df_v = df_ch[mask].sort_values(by='vip', ascending=False)
            
            for _, r in df_v.iterrows():
                try:
                    txt = f"{safe_get(r,1)} {safe_get(r,2)} {safe_get(r,3)} {safe_get(r,4)} {safe_get(r,5)}".upper()
                    if (b_o=="CUALQUIERA" or b_o in safe_get(r,1).upper()) and \
                       (b_d=="CUALQUIERA" or b_d in safe_get(r,2).upper()) and \
                       (b_e=="CUALQUIERA" or b_e==safe_get(r,3)) and (b_q in txt):
                        
                        id_v = sanitizar(r[4]) if len(sanitizar(r[4])) == 11 else sanitizar(r[5])
                        tel_v = sanitizar(r[5]) if id_v != sanitizar(r[5]) else sanitizar(r[4])
                        badge = '<div class="badge-nuevo">NUEVO</div>' if es_nuevo(r[0]) else ''
                        msg = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n✅ *INTERÉS EN UNIDAD*\n📍 RUTA: {r[1]} -> {r[2]}\n🚛 EQUIPO: {r[3]}\n\n¿Está disponible?")
                        
                        st.markdown(f'''<div class="{"card-vip" if r["vip"] else "card-white"}">{badge}
                        {"<div class='vip-label'>⭐ CHOFER VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>EQUIPO:</b> {r[3]} | 🆔 <b>ID:</b> {id_v}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(tel_v)}&text={msg}" target="_blank" class="btn-wsp">✉️ CONTACTAR CHOFER</a></div>''', unsafe_allow_html=True)
                except: continue

# --- TAB CARGAS ---
with tab2:
    f_izq2, f_der2 = st.columns([1, 2.2])
    with f_izq2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_ch", clear_on_submit=True):
            po = st.selectbox("Origen", PROVINCIAS[1:]); plo = st.text_input("Localidad")
            pd = st.selectbox("Destino", PROVINCIAS[1:]); pld = st.text_input("Localidad")
            pe = st.selectbox("Equipo", EQUIPOS[1:]); pi = st.text_input("CUIT/ID"); pw = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{po} ({plo})", "entry.1519265625": f"{pd} ({pld})", "entry.597193898": pe, "entry.1542650763": sanitizar(pi), "entry.1574172378": sanitizar(pw)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with f_der2:
        if not df_ca.empty:
            df_ca['vip'] = df_ca.iloc[:,5].apply(lambda x: str(x).upper().strip() in LISTA_VIPS)
            mask2 = df_ca.iloc[:,0].apply(lambda x: es_fecha_hoy(x, b_f))
            df_v2 = df_ca[mask2].sort_values(by='vip', ascending=False)
            
            for _, r in df_v2.iterrows():
                try:
                    txt2 = f"{safe_get(r,1)} {safe_get(r,2)} {safe_get(r,3)} {safe_get(r,5)}".upper()
                    if (b_o=="CUALQUIERA" or b_o in safe_get(r,1).upper()) and \
                       (b_d=="CUALQUIERA" or b_d in safe_get(r,2).upper()) and (b_q in txt2):
                        
                        badge2 = '<div class="badge-nuevo">NUEVO</div>' if es_nuevo(r[0]) else ''
                        msg2 = urllib.parse.quote(f"─── *RETORNO MATCH VIP* ───\n📦 *CONSULTA POR CARGA*\n🏢 EMPRESA: {r[5]}\n📍 RUTA: {r[1]} -> {r[2]}\n\n¿Sigue disponible?")
                        
                        st.markdown(f'''<div class="{"card-vip" if r["vip"] else "card-white"}">{badge2}
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg2}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a></div>''', unsafe_allow_html=True)
                except: continue

# --- FOOTER ---
st.markdown(f'<div style="text-align:center; color:white; padding:50px; opacity:0.7;"><b>Creado por Ignacio Diaz</b><br>© 2026 RETORNO MATCH VIP</div>', unsafe_allow_html=True)

with st.expander("⚙️ PANEL"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncio = st.text_area("Radar:", st.session_state.anuncio)
        st.markdown(f'<a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}" target="_blank">➕ GESTIONAR VIP</a>', unsafe_allow_html=True)
