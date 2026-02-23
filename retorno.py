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

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS ---
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

hoy = datetime.now().date()
def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True).date() == target
    except: return False

cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, hoy))]) if not df_ca_raw.empty else 0

if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "¡Bienvenido al Sistema VIP!"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 4. ESTILOS PRO & ADAPTABLES (IGNACIO DIAZ) ---
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f; text-align: center; }
    
    /* CARDS ADAPTABLES */
    .card-pro { background: white !important; border-radius: 15px; padding: 15px; margin-bottom: 15px; border-left: 8px solid #3498db; color: #333; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 15px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.4); }
    .card-cosecha { background: #f1f8e9 !important; border-radius: 15px; padding: 15px; margin-bottom: 15px; border-left: 8px solid #2e7d32; border-right: 1px solid #2e7d32; border-top: 1px solid #2e7d32; border-bottom: 1px solid #2e7d32; color: #1b5e20; }
    
    .label-pro { font-size: 12px; font-weight: bold; color: #7f8c8d; text-transform: uppercase; margin-bottom: 2px; }
    .val-pro { font-size: 16px; font-weight: 700; color: #2c3e50; margin-bottom: 8px; }
    .route-txt { font-size: 1.3rem; font-weight: 900; color: #1e3799; text-transform: uppercase; line-height: 1.2; }
    
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px 10px; font-size: 12px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
    
    /* TABS PARA CELULAR */
    @media (max-width: 600px) {
        .stTabs [data-baseweb="tab"] { font-size: 12px !important; padding: 0 5px !important; }
        .route-txt { font-size: 1rem !important; }
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
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ ---
st.markdown("<h2 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h2>", unsafe_allow_html=True)

# Filtros compactos
c1, c2, c3 = st.columns([1,1,1])
with c1: b_o = st.selectbox("🔍 ORIGEN", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO", EQUIPOS)

radar_txt = f"🌾 COSECHA ACTIVA: {cant_camiones} Unidades y {cant_cargas} Cargas -- ⭐ {st.session_state.anuncios} -- Por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- TAB 1 & 2 (Adaptadas) ---
with tab1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        with st.expander("➕ PUBLICAR CARGA"):
            with st.form("f_ca", clear_on_submit=True):
                eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Localidad Origen")
                ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Localidad Destino")
                ec = st.text_input("Mercadería"); en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
                if st.form_submit_button("SUBIR"):
                    requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": ew})
                    st.cache_data.clear(); st.rerun()
    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            for _, r in df_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                    val_a, val_b = limpiar_dato_numerico(r[4]), limpiar_dato_numerico(r[5])
                    cuit, wsp = (val_a, val_b) if len(val_a) == 11 else (val_b, val_a)
                    link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text=Hola, vi su camion {r[3]} en el sistema VIP..."
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-pro"}">{"<div style=\'color:#f1c40f;font-weight:900\'>⭐ VIP</div>" if r["vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><div class="label-pro">Equipo</div><div class="val-pro">{r[3]}</div><a href="{link_wsp}" target="_blank" class="btn-wsp">✉️ CONTACTAR</a></div>', unsafe_allow_html=True)

with tab2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        with st.expander("➕ PUBLICAR CAMIÓN"):
            with st.form("f_ch", clear_on_submit=True):
                op = st.selectbox("Prov. Origen", PROVINCIAS[1:]); ol = st.text_input("Localidad")
                dp = st.selectbox("Prov. Destino", PROVINCIAS[1:]); dl = st.text_input("Localidad")
                et = st.selectbox("Equipo", EQUIPOS[1:]); cid = st.text_input("CUIT"); wn = st.text_input("WhatsApp")
                if st.form_submit_button("SUBIR"):
                    requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{op} ({ol})", "entry.1519265625": f"{dp} ({dl})", "entry.597193898": et, "entry.1542650763": cid, "entry.1574172378": wn})
                    st.cache_data.clear(); st.rerun()
    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            for _, r in df_ca_f.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    link_w = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text=Interesado en carga {r[3]}..."
                    st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-pro"}"><div class="route-txt">{r[1]} ➔ {r[2]}</div><div class="label-pro">Carga</div><div class="val-pro">{r[3]}</div><a href="{link_w}" target="_blank" class="btn-wsp">📩 CONSULTAR</a></div>', unsafe_allow_html=True)

# --- TAB 3: ARRIME PRO (DETALLE Y TARIFA) ---
with tab3:
    st.markdown("<h4 style='color:#f1c40f; text-align:center;'>🌾 OPERATIVOS DE ARRIME</h4>", unsafe_allow_html=True)
    c_a1, c_a2 = st.columns([1, 2.2])
    with c_a1:
        with st.form("f_arr_pro", clear_on_submit=True):
            z_loc = st.text_input("📍 Zona/Localidad")
            g_det = st.text_input("🌾 Detalle (Ej: Soja a Planta X)")
            t_val = st.text_input("💰 Tarifa/Pago")
            w_arr = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR ARRIME"):
                # Formato Pro: Guardamos la tarifa dentro del campo de mercadería
                requests.post(URL_CARGAS_POST, data={"entry.610070407": "ARRIME ZONA", "entry.170847116": z_loc, "entry.576675281": f"ARRIME|{g_det}|{t_val}", "entry.1930562861": "COSECHA", "entry.466540450": w_arr})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()

    with c_a2:
        if not df_ca_raw.empty:
            df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
            if df_arr.empty:
                st.warning("No hay operativos activos.")
            else:
                for _, r in df_arr.iterrows():
                    # Parseamos el detalle y la tarifa
                    parts = str(r[3]).split("|")
                    detalle = parts[1] if len(parts) > 1 else r[3]
                    tarifa = parts[2] if len(parts) > 2 else "A consultar"
                    
                    msg = f"Hola, consulto por el arrime en {r[2]}. Detalle: {detalle}. ¿Está disponible?"
                    l_w = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(msg)}"
                    
                    st.markdown(f'''
                    <div class="card-cosecha">
                        <div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>
                        <div style="display: flex; justify-content: space-between; margin-top:10px;">
                            <div><div class="label-pro">DETALLE</div><div class="val-pro">{detalle}</div></div>
                            <div style="text-align:right;"><div class="label-pro">TARIFA</div><div class="val-pro" style="color:#2e7d32;">{tarifa}</div></div>
                        </div>
                        <a href="{l_w}" target="_blank" class="btn-wsp" style="background-color:#2e7d32;">🚜 POSTULAR CAMIÓN</a>
                    </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f;">© 2026 RETORNO MATCH VIP - Versión Mobile Pro</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️"):
    if st.text_input("PIN", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Radar", st.session_state.anuncios)
