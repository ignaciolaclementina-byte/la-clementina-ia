import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

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

# --- 3. CARGA DE DATOS CON SPINNER (MEJORA 1) ---
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

# Mostrar spinner real durante la carga
with st.spinner("✨ Sincronizando con base de datos VIP de Ignacio Diaz..."):
    df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- LÓGICA DE TIEMPO Y FILTROS ---
hoy = datetime.now().date()

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True).date() == target
    except: return False

def es_nuevo(timestamp_str):
    try:
        ts = pd.to_datetime(timestamp_str, dayfirst=True)
        return (datetime.now() - ts) < timedelta(hours=2)
    except: return False

# --- 4. CONFIGURACIÓN DE PÁGINA Y ESTILOS PREMIUM ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="🚚", layout="wide")

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; border: 2px solid #f1c40f; text-align: center; box-shadow: 0 0 15px rgba(241, 196, 15, 0.3); }
    
    /* MEJORA 5: Cards con bordes Premium */
    .card-white { background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; border: 1px solid #e0e0e0; border-left: 10px solid #3498db; color: #333; transition: 0.3s; }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241, 196, 15, 0.4); border-left: 10px solid #f1c40f; }
    
    /* MEJORA 2: Badge de Nuevo */
    .badge-nuevo { background: #e74c3c; color: white; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: bold; float: right; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% {opacity: 1;} 50% {opacity: 0.5;} 100% {opacity: 1;} }

    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    
    /* Botón Flotante de Compartir (MEJORA 3) */
    .share-btn { position: fixed; bottom: 20px; right: 20px; background: #25D366; color: white; padding: 15px; border-radius: 50%; z-index: 999; box-shadow: 0 4px 10px rgba(0,0,0,0.3); text-decoration: none; font-size: 24px; }
    
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 40px; border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; }
</style>

<a href="https://api.whatsapp.com/send?text=¡Mira esta plataforma para conseguir retornos! 🚚 https://retornomatchvip.streamlit.app" class="share-btn" target="_blank">📲</a>
""", unsafe_allow_html=True)

# --- 5. FUNCIONES DE LIMPIEZA ---
def sanitizar_dato(dato):
    # MEJORA 4: Sanitización completa de CUIT/DNI
    s = str(dato).strip()
    if s.endswith(".0"): s = s[:-2]
    return "".join(filter(str.isdigit, s))

def limpiar_wsp(num):
    clean = sanitizar_dato(num)
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 6. INTERFAZ Y FILTROS ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

# Filtros principales
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)

# MEJORA 2: Buscador libre (Cercanía)
b_q = st.text_input("📍 BUSCADOR RÁPIDO (Ej: San Jorge, Rosario, Empresa X...)", placeholder="Escribe para filtrar resultados al instante...").upper()

# Conteos para el Radar
cant_camiones = len(df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]) if not df_ch_raw.empty else 0
cant_cargas = len(df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))]) if not df_ca_raw.empty else 0

radar_txt = f"🔥 VIVO: {cant_camiones} Camiones y {cant_cargas} Cargas para hoy -- ⭐ {st.session_state.get('anuncios', '¡Bienvenido!')} -- Creado por Ignacio Diaz."
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">{radar_txt}</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 VER CAMIONES (SOY EMPRESA)", "🏢 VER CARGAS (SOY CHOFER)"])

# --- TAB 1: CAMIONES ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f_ca", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("¿Qué carga?"); en = st.text_input("Nombre Empresa")
            ew = st.text_input("WhatsApp", help="Ej: 1123456789 (Sin 0 ni 15)") # MEJORA 1: Ayuda visual
            if st.form_submit_button("SUBIR CARGA"):
                wsp_clean = sanitizar_dato(ew) # MEJORA 4: Sanitizar antes de subir
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": ec, "entry.1930562861": en, "entry.466540450": wsp_clean})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()

    with col_r1:
        if not df_ch_raw.empty:
            df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
            df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f.iterrows():
                # MEJORA 2: Filtro de búsqueda libre integrado
                txt_row = f"{r[1]} {r[2]} {r[3]} {r[4]} {r[5]}".upper()
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and \
                   (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and \
                   (b_e=="CUALQUIERA" or b_e==str(r[3])) and \
                   (b_q in txt_row):
                    
                    cuit = sanitizar_dato(r[4]) if len(sanitizar_dato(r[4])) == 11 else sanitizar_dato(r[5])
                    wsp = sanitizar_dato(r[5]) if cuit == sanitizar_dato(r[4]) else sanitizar_dato(r[4])
                    nuevo_tag = '<span class="badge-nuevo">NUEVO</span>' if es_nuevo(r[0]) else '' # MEJORA 2: Badge

                    texto_wsp = f"─── *RETORNO MATCH VIP* ───\n✅ *SOLICITUD DE UNIDAD*\n\nHola, me interesa su camión:\n📍 *RUTA:* {r[1]} -> {r[2]}\n🚛 *EQUIPO:* {r[3]}\n\n¿Sigue disponible? Gracias."
                    link_wsp = f"https://api.whatsapp.com/send?phone={limpiar_wsp(wsp)}&text={urllib.parse.quote(texto_wsp)}"
                    
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {nuevo_tag}
                        {"<div class='vip-label'>⭐ CHOFER VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>ID/CUIT:</b> {cuit}<br>
                        <a href="{link_wsp}" target="_blank" class="btn-wsp">✉️ ENVIAR PROPUESTA FORMAL</a>
                    </div>''', unsafe_allow_html=True)

# --- TAB 2: CARGAS ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f_ch", clear_on_submit=True):
            o_prov = st.selectbox("Prov. Origen", PROVINCIAS[1:]); o_loc = st.text_input("Loc. Origen")
            d_prov = st.selectbox("Prov. Destino", PROVINCIAS[1:]); d_loc = st.text_input("Loc. Destino")
            e_tipo = st.selectbox("Equipo", EQUIPOS[1:]); cu_id = st.text_input("CUIT/ID")
            wsp_num = st.text_input("WhatsApp", help="Ej: 1123456789 (Sin 0 ni 15)")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o_prov} ({o_loc})", "entry.1519265625": f"{d_prov} ({d_loc})", "entry.597193898": e_tipo, "entry.1542650763": sanitizar_dato(cu_id), "entry.1574172378": sanitizar_dato(wsp_num)})
                st.cache_data.clear(); st.success("¡Publicado!"); time.sleep(1); st.rerun()

    with col_r2:
        if not df_ca_raw.empty:
            df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
            df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
            
            for _, r in df_f2.iterrows():
                txt_row_ca = f"{r[1]} {r[2]} {r[3]} {r[5]}".upper()
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and \
                   (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and \
                   (b_q in txt_row_ca):
                    
                    nuevo_tag = '<span class="badge-nuevo">NUEVO</span>' if es_nuevo(r[0]) else ''
                    texto_wsp_ca = f"─── *RETORNO MATCH VIP* ───\n📦 *INTERÉS EN CARGA*\n\nHola, consulto por la carga:\n🏢 *EMPRESA:* {r[5]}\n📍 *RUTA:* {r[1]} -> {r[2]}\n📦 *CARGA:* {r[3]}\n\n¿Está disponible? Gracias."
                    link_wsp_ca = f"https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={urllib.parse.quote(texto_wsp_ca)}"
                    
                    st.markdown(f'''
                    <div class="{"card-vip" if r["vip"] else "card-white"}">
                        {nuevo_tag}
                        {"<div class='vip-label'>⭐ EMPRESA VIP</div>" if r["vip"] else ""}
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="{link_wsp_ca}" target="_blank" class="btn-wsp">📩 CONSULTAR CARGA</a>
                    </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 18px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="font-style: italic;">No nos responsabilizamos por acuerdos entre partes.</p>
    <p><b>Prohibida la copia total o parcial sin autorización de Ignacio Diaz. © 2026</b></p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ADMIN"):
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Radar:", st.session_state.get('anuncios', ""))
        st.markdown(f'<a href="https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}" target="_blank">➕ GESTIONAR VIP</a>', unsafe_allow_html=True)
