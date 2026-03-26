import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30 
WSP_VENTAS_VIP = "5493401525621"

COORDS_PROV = {
    "BUENOS AIRES": (-34.921, -57.954), "CABA": (-34.603, -58.381), "CATAMARCA": (-28.469, -65.785),
    "CHACO": (-27.451, -58.986), "CHUBUT": (-43.300, -65.102), "CORDOBA": (-31.413, -64.181),
    "CORRIENTES": (-27.469, -58.830), "ENTRE RIOS": (-31.733, -60.529), "FORMOSA": (-26.177, -58.178),
    "JUJUY": (-24.185, -65.299), "LA PAMPA": (-36.616, -64.283), "LA RIOJA": (-29.411, -66.850),
    "MENDOZA": (-32.889, -68.845), "MISIONES": (-27.367, -55.896), "NEUQUEN": (-38.951, -68.059),
    "RIO NEGRO": (-40.813, -62.996), "SALTA": (-24.785, -65.411), "SAN JUAN": (-31.537, -68.536),
    "SAN LUIS": (-33.295, -66.335), "SANTA CRUZ": (-51.622, -69.218), "SANTA FE": (-31.633, -60.700),
    "SANTIAGO DEL ESTERO": (-27.795, -64.263), "TIERRA DEL FUEGO": (-54.801, -68.303), "TUCUMAN": (-26.824, -65.222)
}

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            refs_borradas = df_ca[mask].astype(str).apply(lambda x: x.str.extract(r'REF:(.*)')[0].dropna(), axis=1).stack().tolist()
            df_ca = df_ca[~mask]
            if refs_borradas:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_borradas)]
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except:
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now()
hoy = ahora.date()

# --- FUNCIONES AUXILIARES ---
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def obtener_minutos_desde_publicacion(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True, errors='coerce')
        diff = ahora - ts
        return diff.total_seconds() / 60
    except: return 999

def es_vip(dato):
    val = str(dato).strip().upper().replace(".0", "")
    return val in LISTA_VIPS_GLOBAL

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

def ocultar_telefono(num):
    clean = limpiar_dato_numerico(num)
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def validar_cuit(cuit):
    cuit = "".join(filter(str.isdigit, str(cuit)))
    if len(cuit) != 11: return False
    base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]; aux = sum(int(cuit[i]) * base[i] for i in range(10))
    aux = 11 - (aux % 11)
    if aux == 11: aux = 0
    if aux == 10: aux = 9
    return aux == int(cuit[10])

def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in str(o_str).upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in str(d_str).upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            r = 6371; dlat = math.radians(lat2 - lat1); dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return f"📍 {int(r * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))} km"
        return ""
    except: return ""

def get_card_style(minutos, es_vip_card):
    if es_vip_card: return "card-vip"
    if minutos < 60: return "card-hot"
    if minutos < 180: return "card-medium"
    return "card-old"

# --- INTERFAZ ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# CSS OPTIMIZADO PARA MÓVIL
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    
    /* Ajuste de columnas para móvil */
    [data-testid="column"] { width: 100% !important; flex: 1 1 calc(50% - 1rem) !important; min-width: 45% !important; }
    @media (max-width: 640px) { [data-testid="column"] { min-width: 100% !important; } }

    .stats-card { background: rgba(255,255,255,0.1); border: 1px solid rgba(241, 196, 15, 0.3); border-radius: 12px; padding: 10px; text-align: center; margin-bottom: 10px; }
    .stats-val { font-size: 20px; font-weight: 900; color: #f1c40f; display: block; }
    .stats-label { font-size: 10px; text-transform: uppercase; color: white; }
    
    .card-white, .card-vip, .card-hot, .card-medium, .card-old, .card-cosecha, .card-bloqueada { 
        border-radius: 15px; padding: 18px; margin-bottom: 15px; color: #333; position: relative; 
    }
    .card-hot { background: #fff5f5 !important; border-left: 8px solid #e74c3c !important; }
    .card-medium { background: #f0fff4 !important; border-left: 8px solid #2ecc71 !important; }
    .card-old { background: #f8f9fa !important; border-left: 8px solid #95a5a6 !important; }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; box-shadow: 0px 4px 10px rgba(241,196,15,0.2); }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; }
    .card-bloqueada { background: rgba(0,0,0,0.7) !important; border: 2px dashed #f1c40f !important; color: white !important; text-align: center; }
    
    .route-txt { font-size: 18px; font-weight: 800; color: #1e3799; line-height: 1.2; margin-bottom: 5px; }
    .dist-badge { background: #34495e; color: #f1c40f; padding: 3px 7px; border-radius: 5px; font-size: 11px; float: right; }
    .vip-label { background: #f1c40f; color: black; padding: 2px 10px; border-radius: 10px; font-size: 12px; font-weight: bold; margin-bottom: 8px; display: inline-block; }
    
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; font-size: 15px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 8px; border-radius: 10px; text-decoration: none; display: block; text-align: center; margin-top: 6px; font-size: 13px; }
    
    .stTabs [data-baseweb="tab"] { flex: 1; text-align: center; padding: 10px 5px !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 8px; border-radius: 8px; margin: 10px 0; font-size: 14px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.6); padding: 30px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center; color:white; margin-bottom:0;'>🚛 RETORNO MATCH VIP</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#f1c40f; font-size:12px;'>BY IGNACIO DIAZ</p>", unsafe_allow_html=True)

# --- STATS COMPACTAS ---
cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

cstats1, cstats2, cstats3 = st.columns(3)
with cstats1: st.markdown(f'<div class="stats-card"><span class="stats-val">{cant_camiones+cant_cargas}</span><span class="stats-label">Hoy</span></div>', unsafe_allow_html=True)
with cstats2: st.markdown(f'<div class="stats-card"><span class="stats-val">{len(LISTA_VIPS_GLOBAL)}</span><span class="stats-label">VIPs</span></div>', unsafe_allow_html=True)
with cstats3: st.markdown(f'<div class="stats-card"><span class="stats-val">LIVE</span><span class="stats-label">Red</span></div>', unsafe_allow_html=True)

# --- LOGIN & FILTROS ---
with st.expander("🔑 ACCESO VIP / FILTROS"):
    user_cuit = st.text_input("CUIT:", "").strip()
    soy_vip_actual = es_vip(user_cuit) if (user_cuit and validar_cuit(user_cuit)) else False
    if soy_vip_actual: st.success("ACCESO VIP ACTIVO")
    
    PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
    EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]
    
    f_col1, f_col2 = st.columns(2)
    b_fecha = f_col1.date_input("Fecha:", hoy)
    b_e = f_col2.selectbox("Equipo:", EQUIPOS)
    b_o = st.selectbox("Origen:", PROVINCIAS)
    b_d = st.selectbox("Destino:", PROVINCIAS)
    busqueda_libre = st.text_input("Palabra clave:", "").upper()

radar_txt = f"{st.session_state.get('anuncios', '¡Bienvenido!')} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee>{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1: CAMIONES ---
with tab1:
    with st.expander("➕ PUBLICAR MI CARGA"):
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                st.cache_data.clear(); st.rerun()

    if not df_ch_raw.empty:
        df_ch_raw['vip'] = df_ch_raw.apply(lambda r: (es_vip(r[4]) or es_vip(r[5])) if len(r) > 5 else False, axis=1)
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f.iterrows():
            if len(r) < 6: continue
            minutos_pub = obtener_minutos_desde_publicacion(r[0])
            distancia = calcular_distancia(str(r[1]), str(r[2]))
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])) and (busqueda_libre in str(r).upper()):
                val_a, val_b = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                cuit, wsp = (val_a, val_b) if len(val_a) == 11 else (val_b, val_a)
                link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text=" + urllib.parse.quote(f"🤝 *CONTACTO COMERCIAL*\n\nConsulta por unidad:\n📍 {r[1]} ➔ {r[2]}\n🚛 EQUIPO: {r[3]}")
                card_class = get_card_style(minutos_pub, r['vip'])
                st.markdown(f'<div class="{card_class}">{f"<span class=\'dist-badge\'>{distancia}</span>" if distancia else ""}{"<div class=\'vip-label\'>⭐ CHOFER VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>Equip:</b> {r[3]} | 🆔 {cuit}<br><a href="{link_wsp}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with tab2:
    with st.expander("➕ PUBLICAR MI CAMIÓN"):
        with st.form("f_ch", clear_on_submit=True):
            o_prov = st.selectbox("Prov. Origen", PROVINCIAS[1:]); o_loc = st.text_input("Loc. Origen")
            d_prov = st.selectbox("Prov. Destino", PROVINCIAS[1:]); d_loc = st.text_input("Loc. Destino")
            e_tipo = st.selectbox("Equipo", EQUIPOS[1:]); cu_id = st.text_input("CUIT"); wsp_num = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CAMIÓN"):
                if validar_cuit(cu_id):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o_prov} ({o_loc})", "entry.1519265625": f"{d_prov} ({d_loc})", "entry.597193898": e_tipo, "entry.1542650763": cu_id, "entry.1574172378": wsp_num})
                    st.cache_data.clear(); st.rerun()

    if not df_ca_raw.empty:
        df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip) if len(df_ca_raw.columns) > 5 else False
        df_ca_filtered = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        df_f2 = df_ca_filtered[df_ca_filtered.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f2.iterrows():
            if len(r) < 6: continue
            minutos = obtener_minutos_desde_publicacion(r[0])
            distancia = calcular_distancia(str(r[1]), str(r[2]))
            if minutos < TIEMPO_EXCLUSIVO_MIN and not soy_vip_actual:
                st.markdown(f'<div class="card-bloqueada">🔒 EXCLUSIVO VIP<br><small>Disponible en {int(TIEMPO_EXCLUSIVO_MIN - minutos)} min</small><br><a href="https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}" style="color:#f1c40f;">⭐ ACTIVAR</a></div>', unsafe_allow_html=True)
            elif (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (busqueda_libre in str(r).upper()):
                link_wsp_ca = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=" + urllib.parse.quote(f"🚛 *CONSULTA DE CARGA*\n📍 ORIGEN: {r[1]}\n🏁 DESTINO: {r[2]}\n📦 CARGA: {r[3]}")
                link_share = f"https://api.whatsapp.com/send?text=" + urllib.parse.quote(f"📢 *NUEVA CARGA*\n📍 {r[1]} ➔ {r[2]}\n📦 {r[3]}\n🏢 {r[5]}")
                card_class = get_card_style(minutos, r['vip'])
                st.markdown(f'<div class="{card_class}">{f"<span class=\'dist-badge\'>{distancia}</span>" if distancia else ""}{"<div class=\'vip-label\'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>Carga:</b> {r[3]} | 🏢 {r[5]}<br><a href="{link_wsp_ca}" target="_blank" class="btn-wsp">📩 CONSULTAR</a><a href="{link_share}" target="_blank" class="btn-share">📢 DIFUNDIR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME ---
with tab3:
    with st.expander("➕ PUBLICAR ARRIME"):
        with st.form("f_arr", clear_on_submit=True):
            z_loc = st.text_input("📍 Zona"); g_det = st.text_input("🌾 Detalle"); t_val = st.text_input("💰 Tarifa"); w_arr = st.text_input("WhatsApp")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z_loc, "entry.576675281": f"ARRIME|{g_det}|{t_val}", "entry.1930562861": "COSECHA", "entry.466540450": w_arr})
                st.cache_data.clear(); st.rerun()
    if not df_ca_raw.empty:
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        for idx, r in df_arrime.iterrows():
            if len(r) < 5: continue
            st.markdown(f'<div class="card-cosecha"><div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>{r[3]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">🚜 CONTACTAR</a></div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 16px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP</p>
</div>
""", unsafe_allow_html=True)

# --- ADMIN ---
with st.expander("⚙️"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.session_state.anuncios = st.text_area("Radar:", st.session_state.get('anuncios', ''))
        if st.button("Limpiar Caché"): st.cache_data.clear(); st.rerun()
