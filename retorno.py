import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
import hashlib
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# 1. CONFIGURACIÓN  (CREADO POR IGNACIO DIAZ - MEJORADO 2026)
# ============================================================
SHEET_ID        = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES    = "1392659349"
GID_CARGAS      = "1267917528"
GID_VIP         = "968995524"

URL_CARGAS_POST   = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

# PIN desde secrets (si no existe, usa el valor de fallback)
try:
    ADMIN_PIN = st.secrets["ADMIN_PIN"]
except Exception:
    ADMIN_PIN = "1323"

TIEMPO_EXCLUSIVO_MIN = 30
WSP_VENTAS_VIP       = "5493406649346"
HORAS_EXPIRACION     = 72   # ocultar publicaciones con más de X horas

# Peajes aproximados entre zonas (solo referencia)
PEAJES_REF = {
    "ROSARIO": 3500, "CORDOBA": 5200, "BAHIA BLANCA": 7800,
    "TUCUMAN": 9500, "SALTA": 12000, "SANTA FE": 2800,
    "PARANA": 3200, "CAMPANA": 6500, "ZARATE": 6200,
}

# ============================================================
# 2. BASE DE CIUDADES
# ============================================================
COORDS_CIUDADES = {
    "TODAS": (0, 0),
    "SAN JORGE (SF)": (-31.896, -61.859),   "ROSARIO (SF)": (-32.946, -60.639),
    "SANTA FE (SF)": (-31.633, -60.700),    "RAFAELA (SF)": (-31.250, -61.486),
    "CAÑADA DE GOMEZ (SF)": (-32.816, -61.395), "VENADO TUERTO (SF)": (-33.745, -61.968),
    "SAN CRISTOBAL (SF)": (-30.310, -61.237),   "AVELLANEDA (SF)": (-29.117, -59.658),
    "CRISPI (SF)": (-31.721, -61.916),      "SASTRE (SF)": (-31.766, -61.828),
    "CARLOS PELLEGRINI (SF)": (-32.052, -61.789), "PIAMONTE (SF)": (-32.152, -61.986),
    "TIMBUES (SF)": (-32.668, -60.751),     "PTO GRAL SAN MARTIN (SF)": (-32.745, -60.732),
    "SAN LORENZO (SF)": (-32.746, -60.734),
    "CORDOBA (CBA)": (-31.413, -64.181),    "SAN FRANCISCO (CBA)": (-31.427, -62.082),
    "RIO CUARTO (CBA)": (-33.123, -64.348), "VILLA MARIA (CBA)": (-32.407, -63.240),
    "JESUS MARIA (CBA)": (-30.981, -64.093),"MARCOS JUAREZ (CBA)": (-32.697, -62.106),
    "BAHIA BLANCA (BA)": (-38.718, -62.266),"QUEQUEN (BA)": (-38.541, -58.713),
    "CAMPANA (BA)": (-34.163, -58.959),     "ZARATE (BA)": (-34.096, -59.024),
    "RAMALLO (BA)": (-33.483, -60.000),     "PERGAMINO (BA)": (-33.891, -60.573),
    "PARANA (ER)": (-31.733, -60.529),      "VICTORIA (ER)": (-32.624, -60.155),
    "SGO DEL ESTERO": (-27.795, -64.263),   "TUCUMAN": (-26.824, -65.222),
    "SALTA": (-24.785, -65.411),
}

# ============================================================
# 3. GESTIÓN DE SESIÓN
# ============================================================
defaults = {
    "admin_mode": False,
    "anuncios": "¡Bienvenido al Sistema VIP!",
    "situacion_actual": "Sin reportes de demoras por el momento.",
    "search_query": "",
    "reportes_puerto": "Normal - Sin demoras reportadas en accesos.",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================================
# 4. CARGA DE DATOS  (ttl=60 para no saturar Sheets)
# ============================================================
@st.cache_data(ttl=60)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(
            f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}"
        ).fillna("-")
        df_ca = pd.read_csv(
            f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}"
        ).fillna("-")

        if not df_ca.empty:
            mask_borrado = df_ca.iloc[:, 1].astype(str).str.contains("BORRADO", case=False)
            refs_a_borrar = [
                re.search(r"REF:(.*)", str(cell)).group(1).strip()
                for row in df_ca[mask_borrado].values
                for cell in row
                if re.search(r"REF:(.*)", str(cell))
            ]
            df_ca = df_ca[~mask_borrado]
            if refs_a_borrar:
                df_ca = df_ca[~df_ca.iloc[:, 0].astype(str).isin(refs_a_borrar)]

        vips = []
        try:
            url_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&t={t}"
            df_v = pd.read_csv(url_vip, header=None)
            if not df_v.empty:
                vips = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except Exception:
            pass

        return df_ch, df_ca, vips
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# ============================================================
# 5. FUNCIONES AUXILIARES
# ============================================================
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    if not clean:
        return "5491111111111"
    clean = clean[1:] if clean.startswith("0") else clean
    clean = clean.replace("15", "", 1) if clean.startswith("15") else clean
    return "549" + clean if not clean.startswith("549") else clean

def generar_wsp_link(num, origen, destino, es_chofer=True):
    clean_num = limpiar_wsp(num)
    msg = (
        f"Hola! Vi tu camión de {origen} a {destino} en Retorno Match. ¿Tenés carga?"
        if es_chofer
        else f"Hola! Me interesa la carga de {origen} a {destino} que publicaste en Retorno Match."
    )
    return f"https://api.whatsapp.com/send?phone={clean_num}&text={urllib.parse.quote(msg)}"

def link_ventas_vip(cuit=""):
    msg = f"Hola Ignacio! Quiero solicitar el acceso VIP para el CUIT: {cuit}"
    return f"https://api.whatsapp.com/send?phone={WSP_VENTAS_VIP}&text={urllib.parse.quote(msg)}"

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).split(".")[0]))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def formatear_fecha(timestamp_str):
    try:
        dt = pd.to_datetime(timestamp_str)
        ahora = datetime.now()
        diff = ahora - dt
        if diff.days > 0:
            return f"Hace {diff.days}d"
        horas = diff.seconds // 3600
        if horas > 0:
            return f"Hace {horas}h"
        minutos = (diff.seconds % 3600) // 60
        return f"Hace {minutos}m"
    except Exception:
        return "Reciente"

def esta_expirada(timestamp_str, horas=HORAS_EXPIRACION):
    """Devuelve True si la publicación supera las horas de expiración."""
    try:
        dt = pd.to_datetime(timestamp_str)
        return (datetime.now() - dt).total_seconds() > horas * 3600
    except Exception:
        return False

def badge_fecha(timestamp_str):
    """Devuelve el badge de tiempo con color según antigüedad."""
    try:
        dt = pd.to_datetime(timestamp_str)
        diff_h = (datetime.now() - dt).total_seconds() / 3600
        texto = formatear_fecha(timestamp_str)
        if diff_h > 48:
            color = "#e74c3c"
        elif diff_h > 24:
            color = "#f39c12"
        else:
            color = "#8b949e"
        return f'<div class="badge-time" style="color:{color};">{texto}</div>'
    except Exception:
        return '<div class="badge-time">Reciente</div>'

def calcular_distancia(origen, destino):
    lat1, lon1 = COORDS_CIUDADES.get(origen, (0, 0))
    lat2, lon2 = COORDS_CIUDADES.get(destino, (0, 0))
    if lat1 == 0 or lat2 == 0:
        return 0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def estimar_peajes(destino):
    for ciudad, valor in PEAJES_REF.items():
        if ciudad in str(destino).upper():
            return valor
    return 2000  # mínimo base

def obtener_clima(ciudad):
    if ciudad == "TODAS" or ciudad not in COORDS_CIUDADES:
        return None
    try:
        lat, lon = COORDS_CIUDADES[ciudad]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=True"
        res = requests.get(url, timeout=4).json()
        temp = res["current_weather"]["temperature"]
        code = res["current_weather"]["weathercode"]
        codigos = {
            0: "☀️ Despejado", 1: "🌤️ Liger. Nublado", 2: "⛅ Nublado", 3: "☁️ Cubierto",
            45: "🌫️ Niebla", 48: "🌫️ Niebla", 51: "🌧️ Llovizna", 53: "🌧️ Llovizna",
            61: "🌧️ Lluvia Leve", 63: "🌧️ Lluvia", 65: "🌧️ Lluvia Fuerte",
            80: "🌦️ Chubascos", 95: "⚡ Tormenta", 96: "⚡ Tormenta", 99: "⚡ Tormenta",
        }
        return f"{codigos.get(code, '🌡️ Templado')} {temp}°C"
    except Exception:
        return "N/A"

def hash_cuit(cuit):
    return hashlib.sha256(cuit.encode()).hexdigest()

# ============================================================
# 6. ESTILOS
# ============================================================
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #adbac7; }

    .card-white {
        background: #1c2128; color: #adbac7; padding: 15px; border-radius: 12px;
        margin-bottom: 12px; border: 1px solid #30363d; border-left: 6px solid #3498db;
        position: relative;
    }
    .card-urgente {
        background: #2d1b1b; color: #ff6b6b; padding: 15px; border-radius: 12px;
        margin-bottom: 12px; border: 1px solid #6e2a2a; animation: pulse 2s infinite;
        border-left: 6px solid #ff4b4b; position: relative;
    }
    .card-cosecha {
        background: #1c2a1c; border: 1px solid #2d4d2d; color: #8ebf8e;
        padding: 15px; border-radius: 12px; margin-bottom: 12px;
        border-left: 6px solid #4caf50; position: relative;
    }
    .card-expirada {
        background: #1a1a1a; color: #555; padding: 15px; border-radius: 12px;
        margin-bottom: 12px; border: 1px dashed #333; border-left: 6px solid #555;
        position: relative; opacity: 0.6;
    }
    .vip-access-box {
        background: #1c2128; border: 2px solid #f1c40f; padding: 20px;
        border-radius: 15px; margin-bottom: 25px; text-align: center;
        box-shadow: 0px 4px 15px rgba(241,196,15,0.2);
    }
    .port-report-box {
        background: #161b22; border: 1px solid #30363d; border-top: 4px solid #539bf5;
        padding: 15px; border-radius: 12px; margin-bottom: 20px;
    }
    .badge-time {
        position: absolute; top: 10px; right: 10px; font-size: 0.75rem;
        background: #30363d; padding: 2px 8px; border-radius: 10px; color: #8b949e;
    }
    .route-txt {
        font-size: 1.1rem; font-weight: 800; color: #539bf5;
        text-transform: uppercase; line-height: 1.2;
    }
    .status-bar {
        background: #161b22; border: 1px solid #30363d; border-left: 4px solid #f1e05a;
        padding: 10px; border-radius: 8px; margin-bottom: 20px; color: #e6edf3;
    }
    .counter-box {
        background: #21262d; border: 1px solid #30363d; border-radius: 8px;
        padding: 8px 14px; font-size: 0.85rem; color: #8b949e;
        display: inline-block; margin-bottom: 10px;
    }
    .metric-card {
        background: #1c2128; border: 1px solid #30363d; border-radius: 12px;
        padding: 20px; text-align: center;
    }
    .stButton>button { width: 100%; border-radius: 8px; }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(255,75,75,0.4); }
        70%  { box-shadow: 0 0 0 10px rgba(255,75,75,0); }
        100% { box-shadow: 0 0 0 0 rgba(255,75,75,0); }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 7. SIDEBAR ADMIN
# ============================================================
with st.sidebar:
    st.title("🛡️ Gestión")
    pin_input = st.text_input("PIN Admin", type="password")
    if pin_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("MODO EDITOR ACTIVO")
        st.session_state.anuncios         = st.text_area("📢 Mensajes:", st.session_state.anuncios)
        st.session_state.situacion_actual = st.text_area("🚛 Sit. Actual (Demoras):", st.session_state.situacion_actual)
        st.session_state.reportes_puerto  = st.text_area("🚢 Reporte Puertos:", st.session_state.reportes_puerto)
        if st.button("♻️ Forzar Sincronización"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.session_state.admin_mode = False

    st.divider()
    st.caption("📋 Acerca de")
    st.caption("Creado por Ignacio Diaz - 2026")
    st.caption(f"🕐 Actualizado: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# 8. CABECERA
# ============================================================
st.title("🚛 RETORNO MATCH VIP")
st.markdown(
    f'<div style="background:#21262d; border:1px solid #30363d; padding:10px; border-radius:10px;'
    f' text-align:center; margin-bottom:15px;">'
    f'<marquee scrollamount="6" style="color:#539bf5;"><b>{st.session_state.anuncios}</b></marquee>'
    f'</div>',
    unsafe_allow_html=True,
)

# ============================================================
# 9. SECCIÓN VIP
# ============================================================
with st.container():
    st.markdown('<div class="vip-access-box">', unsafe_allow_html=True)
    st.subheader("🔑 ACCESO VIP")
    user_cuit     = st.text_input(
        "Ingrese su CUIT para desbloquear números de contacto:",
        placeholder="Ej: 20304445556",
        label_visibility="collapsed",
    ).strip()
    es_user_vip = user_cuit in LISTA_VIPS_GLOBAL

    if user_cuit:
        if es_user_vip:
            st.markdown(
                '<p style="color:#2ecc71; font-weight:bold; margin-top:10px;">✅ ACCESO VIP ACTIVO - Contactos Desbloqueados</p>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<p style="color:#e74c3c; margin-top:10px;">❌ CUIT no registrado.</p>', unsafe_allow_html=True)
            st.markdown(
                f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" style="color:#f1c40f; text-decoration:none; font-weight:bold;">'
                f'👉 Click aquí para solicitar el acceso por WhatsApp</a>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Complete su CUIT para ver los teléfonos de contacto.")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 10. REPORTE DE PUERTOS
# ============================================================
st.markdown('<div class="port-report-box">', unsafe_allow_html=True)
cp1, cp2 = st.columns([1, 4])
cp1.markdown("<h2 style='text-align:center; margin:0;'>🚢</h2>", unsafe_allow_html=True)
cp2.markdown(
    f"<small style='color:#8b949e;'>ESTADO DE PUERTOS (ACTUALIZADO):</small><br><b>{st.session_state.reportes_puerto}</b>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 11. FILTROS
# ============================================================
col_search, col_fast = st.columns([2, 1])
busqueda_libre = col_search.text_input(
    "🔎 BUSCAR:",
    value=st.session_state.search_query,
    placeholder="Localidad, Empresa...",
).upper()
if col_fast.button("🧹 Limpiar Filtros"):
    st.session_state.search_query = ""
    st.rerun()

st.write("Filtros Rápidos:")
cf1, cf2, cf3, cf4 = st.columns(4)
if cf1.button("🚢 PUERTOS"):      st.session_state.search_query = "PUERTO";   st.rerun()
if cf2.button("🌻 ACEITERA"):     st.session_state.search_query = "COFCO";    st.rerun()
if cf3.button("🌽 MAIZ"):         st.session_state.search_query = "MAIZ";     st.rerun()
if cf4.button("📍 SAN JORGE"):    st.session_state.search_query = "SAN JORGE";st.rerun()

filtro_loc = st.selectbox("📍 Filtrar por Ciudad Base:", list(COORDS_CIUDADES.keys()))

# Situación + Clima
st.write("")
col_sit, col_clima = st.columns([3, 1])
col_sit.markdown(
    f'<div class="status-bar">⚠️ <b>SITUACIÓN ACTUAL:</b> {st.session_state.situacion_actual}</div>',
    unsafe_allow_html=True,
)
ciudad_clima = "SAN JORGE (SF)" if filtro_loc == "TODAS" else filtro_loc
col_clima.markdown(
    f'<div class="status-bar" style="border-left-color:#3498db; text-align:center;">'
    f'{obtener_clima(ciudad_clima)}<br><small>{ciudad_clima}</small></div>',
    unsafe_allow_html=True,
)

# ============================================================
# 12. TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 COSECHA", "📊 COSTOS", "📈 ESTADÍSTICAS"])

lock_btn_html = (
    f'<a href="{link_ventas_vip(user_cuit)}" target="_blank" '
    f'style="background:#444; color:#f1c40f !important; padding:12px; border-radius:8px; '
    f'text-decoration:none; display:block; text-align:center; font-weight:bold; '
    f'margin-top:10px; font-size:0.85rem; border:1px solid #f1c40f;">⭐ SOLICITAR ACCESO VIP</a>'
)

def empty_state(msg="No hay publicaciones activas en este momento."):
    st.markdown(
        f'<div style="text-align:center; padding:40px; color:#555; border:1px dashed #333; '
        f'border-radius:12px; margin-top:10px;">'
        f'<p style="font-size:2rem;">📭</p><p>{msg}</p></div>',
        unsafe_allow_html=True,
    )

# ─── TAB 1: CAMIONES ────────────────────────────────────────
with tab1:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR CAMIÓN"):
                with st.form("f_ch", clear_on_submit=True):
                    o_p = st.text_input("Origen").upper()
                    d_p = st.text_input("Destino").upper()
                    eq  = st.text_input("Equipo")
                    cu  = st.text_input("CUIT")
                    ws  = st.text_input("WhatsApp")
                    if st.form_submit_button("🚀 PUBLICAR"):
                        if o_p and d_p:
                            requests.post(URL_CHOFERES_POST, data={
                                "entry.1304806144": o_p, "entry.1519265625": d_p,
                                "entry.597193898": eq, "entry.1542650763": cu,
                                "entry.1574172378": ws,
                            })
                            st.cache_data.clear()
                            st.rerun()

    with c2:
        if not df_ch_raw.empty:
            filas_visibles = [
                r for _, r in df_ch_raw.iterrows()
                if busqueda_libre in str(r).upper()
                and (filtro_loc == "TODAS" or filtro_loc in str(r.iloc[1]).upper())
            ]
            # Separar expiradas
            activas   = [r for r in filas_visibles if not esta_expirada(r.iloc[0])]
            expiradas = [r for r in filas_visibles if esta_expirada(r.iloc[0])]

            st.markdown(
                f'<div class="counter-box">Mostrando <b>{len(activas)}</b> activas '
                f'/ {len(expiradas)} vencidas (>{HORAS_EXPIRACION}h)</div>',
                unsafe_allow_html=True,
            )

            if not activas:
                empty_state("No hay camiones disponibles con los filtros actuales.")
            for r in activas:
                btn = (
                    f'<a href="{generar_wsp_link(r.iloc[5], r.iloc[1], r.iloc[2], True)}" target="_blank" '
                    f'style="background:#238636; color:white !important; padding:12px; border-radius:8px; '
                    f'text-decoration:none; display:block; text-align:center; font-weight:bold; '
                    f'margin-top:10px; font-size:0.9rem;">OFERTAR CARGA</a>'
                    if es_user_vip or st.session_state.admin_mode
                    else lock_btn_html
                )
                st.markdown(
                    f'<div class="card-white">'
                    f'{badge_fecha(r.iloc[0])}'
                    f'<span class="route-txt">📍 {r.iloc[1]} <br>➔ {r.iloc[2]}</span><br>'
                    f'<b>EQ:</b> {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[5])}'
                    f'{btn}</div>',
                    unsafe_allow_html=True,
                )

            if expiradas:
                with st.expander(f"🕓 Ver publicaciones vencidas ({len(expiradas)})"):
                    for r in expiradas:
                        st.markdown(
                            f'<div class="card-expirada">'
                            f'<span style="font-size:0.8rem;">⏰ VENCIDA - {formatear_fecha(r.iloc[0])}</span><br>'
                            f'<span class="route-txt" style="color:#555;">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>'
                            f'<b>EQ:</b> {r.iloc[3]}</div>',
                            unsafe_allow_html=True,
                        )
        else:
            empty_state("No se pudieron cargar los camiones.")

# ─── TAB 2: CARGAS ──────────────────────────────────────────
with tab2:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ NUEVA CARGA"):
                with st.form("f_ca", clear_on_submit=True):
                    o   = st.text_input("Carga").upper()
                    d   = st.text_input("Descarga").upper()
                    m   = st.text_input("Mercadería")
                    en  = st.text_input("Empresa")
                    w   = st.text_input("WhatsApp")
                    urg = st.checkbox("🚨 URGENTE")
                    if st.form_submit_button("💼 PUBLICAR"):
                        if o and d:
                            requests.post(URL_CARGAS_POST, data={
                                "entry.610070407": o, "entry.170847116": d,
                                "entry.576675281": f"⚠️URGENTE: {m}" if urg else m,
                                "entry.1930562861": en, "entry.466540450": w,
                            })
                            st.cache_data.clear()
                            st.rerun()

    with c2:
        if not df_ca_raw.empty:
            df_ca_v = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains("ARRIME", case=False)]
            filas_visibles = [r for _, r in df_ca_v.iterrows() if busqueda_libre in str(r).upper()]
            activas   = [r for r in filas_visibles if not esta_expirada(r.iloc[0])]
            expiradas = [r for r in filas_visibles if esta_expirada(r.iloc[0])]

            st.markdown(
                f'<div class="counter-box">Mostrando <b>{len(activas)}</b> activas '
                f'/ {len(expiradas)} vencidas (>{HORAS_EXPIRACION}h)</div>',
                unsafe_allow_html=True,
            )

            if not activas:
                empty_state("No hay cargas publicadas con los filtros actuales.")
            for r in activas:
                estilo    = "card-urgente" if "URGENTE" in str(r.iloc[3]).upper() else "card-white"
                btn_wsp   = (
                    f'<a href="{generar_wsp_link(r.iloc[4], r.iloc[1], r.iloc[2], False)}" target="_blank" '
                    f'style="flex:2; background:#2980b9; color:white !important; padding:12px; border-radius:8px; '
                    f'text-decoration:none; text-align:center; font-weight:bold; font-size:0.9rem;">SOLICITAR VIAJE</a>'
                    if es_user_vip or st.session_state.admin_mode
                    else lock_btn_html
                )
                link_r    = (
                    f"https://www.google.com/maps/dir/?api=1"
                    f"&origin={urllib.parse.quote(str(r.iloc[1]))}"
                    f"&destination={urllib.parse.quote(str(r.iloc[2]))}"
                    f"&travelmode=driving"
                )
                st.markdown(
                    f'<div class="{estilo}">'
                    f'{badge_fecha(r.iloc[0])}'
                    f'<div class="route-txt">{r.iloc[1]} <br>➔ {r.iloc[2]}</div>'
                    f'<div style="font-size:0.9rem; margin:8px 0; opacity:0.9;">📦 <b>{r.iloc[3]}</b> | 🏢 {r.iloc[5]}</div>'
                    f'<div style="display:flex; gap:8px;">{btn_wsp}'
                    f'<a href="{link_r}" target="_blank" style="flex:1; background:#30363d; color:#539bf5 !important; '
                    f'padding:12px; border-radius:8px; text-decoration:none; text-align:center; font-weight:bold; '
                    f'font-size:0.9rem; border:1px solid #539bf5;">🗺️ RUTA</a>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

            if expiradas:
                with st.expander(f"🕓 Ver cargas vencidas ({len(expiradas)})"):
                    for r in expiradas:
                        st.markdown(
                            f'<div class="card-expirada">'
                            f'<span style="font-size:0.8rem;">⏰ VENCIDA - {formatear_fecha(r.iloc[0])}</span><br>'
                            f'<span class="route-txt" style="color:#555;">{r.iloc[1]} ➔ {r.iloc[2]}</span><br>'
                            f'📦 {r.iloc[3]}</div>',
                            unsafe_allow_html=True,
                        )
        else:
            empty_state("No se pudieron cargar las cargas.")

# ─── TAB 3: COSECHA ─────────────────────────────────────────
with tab3:
    c1, c2 = st.columns([1, 2.2])
    with c1:
        if st.session_state.admin_mode:
            with st.expander("➕ REGISTRAR ARRIME"):
                with st.form("f_arr", clear_on_submit=True):
                    loc_arr = st.text_input("Localidad").upper()
                    det_arr = st.text_input("Detalle")
                    wsp_arr = st.text_input("WhatsApp")
                    if st.form_submit_button("🌾 PUBLICAR"):
                        requests.post(URL_CARGAS_POST, data={
                            "entry.610070407": "ARRIME ZONA", "entry.170847116": loc_arr,
                            "entry.576675281": det_arr, "entry.466540450": wsp_arr,
                        })
                        st.cache_data.clear()
                        st.rerun()

    with c2:
        if not df_ca_raw.empty:
            df_arr = df_ca_raw[df_ca_raw.iloc[:, 1].astype(str).str.contains("ARRIME", case=False)]
            filas_visibles = [r for _, r in df_arr.iterrows() if busqueda_libre in str(r).upper()]

            st.markdown(
                f'<div class="counter-box">Mostrando <b>{len(filas_visibles)}</b> zonas de arrime</div>',
                unsafe_allow_html=True,
            )

            if not filas_visibles:
                empty_state("No hay arrimes publicados en este momento.")
            for r in filas_visibles:
                btn_c = (
                    f'<a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r.iloc[4])}" target="_blank" '
                    f'style="background:#238636; color:white !important; padding:12px; border-radius:8px; '
                    f'text-decoration:none; display:block; text-align:center; font-weight:bold; '
                    f'margin-top:10px; font-size:0.9rem;">CONTACTAR</a>'
                    if es_user_vip or st.session_state.admin_mode
                    else lock_btn_html
                )
                st.markdown(
                    f'<div class="card-cosecha">'
                    f'{badge_fecha(r.iloc[0])}'
                    f'<div style="font-weight:bold; font-size:1.1rem;">📍 ZONA: {r.iloc[2]}</div>'
                    f'🌾 {r.iloc[3]} | 📱 {ocultar_telefono(r.iloc[4])}'
                    f'{btn_c}</div>',
                    unsafe_allow_html=True,
                )

# ─── TAB 4: CALCULADOR DE COSTOS ────────────────────────────
with tab4:
    st.subheader("📊 Estimador de Costos de Viaje")

    col_orig, col_dest = st.columns(2)
    o_c = col_orig.selectbox("📍 Desde", list(COORDS_CIUDADES.keys()), key="ca1")
    d_c = col_dest.selectbox("📍 Hasta", list(COORDS_CIUDADES.keys()), key="ca2")

    st.markdown("---")
    cc1, cc2, cc3 = st.columns(3)
    t_km         = cc1.number_input("💲 Tarifa $/KM",         value=1300, step=50)
    precio_gasoil = cc2.number_input("⛽ Precio Gasoil ($/Lt)", value=1050, step=10)
    consumo_lt   = cc3.number_input("🚛 Consumo (Lt/100KM)",  value=38,   step=1)

    cc4, cc5 = st.columns(2)
    incluir_peajes = cc4.checkbox("🛣️ Incluir peajes estimados", value=True)
    ganancia_pct   = cc5.slider("📈 % Ganancia deseada",         0, 50, 20)

    dist = calcular_distancia(o_c, d_c)

    if dist > 0 and o_c != "TODAS" and d_c != "TODAS":
        dist_r      = dist * 1.22       # factor de ruta real
        costo_km    = dist_r * t_km
        costo_comb  = (dist_r / 100) * consumo_lt * precio_gasoil
        costo_peaje = estimar_peajes(d_c) if incluir_peajes else 0
        subtotal    = costo_comb + costo_peaje
        ganancia    = subtotal * (ganancia_pct / 100)
        total_sug   = costo_km + ganancia

        st.markdown("---")
        st.markdown("### 📋 Resumen del Viaje")

        m1, m2, m3 = st.columns(3)
        m1.metric("📏 Distancia Estimada", f"{dist_r:.0f} KM")
        m2.metric("⏱️ Tiempo Aprox.",      f"{dist_r/80:.1f} hs")
        m3.metric("⛽ Combustible Est.",   f"{(dist_r/100)*consumo_lt:.0f} Lt")

        st.markdown("---")
        st.markdown("### 💰 Desglose de Costos")

        datos_costo = {
            "Concepto":  ["Flete base ($/KM)", "Combustible", "Peajes", "Ganancia deseada"],
            "Monto ($)": [costo_km, costo_comb, costo_peaje, ganancia],
        }
        df_costos = pd.DataFrame(datos_costo)

        # Tabla estilizada
        col_tabla, col_grafico = st.columns([1, 1])
        with col_tabla:
            for _, fila in df_costos.iterrows():
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; padding:10px; '
                    f'background:#1c2128; border-radius:8px; margin-bottom:6px; border:1px solid #30363d;">'
                    f'<span>{fila["Concepto"]}</span>'
                    f'<span style="color:#539bf5; font-weight:bold;">${fila["Monto ($)"]:,.0f}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(
                f'<div style="display:flex; justify-content:space-between; padding:14px; '
                f'background:#162032; border-radius:8px; border:2px solid #539bf5; margin-top:8px;">'
                f'<span style="font-weight:bold; font-size:1.1rem;">💎 TOTAL SUGERIDO</span>'
                f'<span style="color:#2ecc71; font-weight:bold; font-size:1.2rem;">${total_sug:,.0f}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col_grafico:
            fig_pie = px.pie(
                df_costos,
                names="Concepto",
                values="Monto ($)",
                hole=0.45,
                color_discrete_sequence=["#539bf5", "#2ecc71", "#f39c12", "#e74c3c"],
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#adbac7",
                margin=dict(t=10, b=10, l=10, r=10),
                showlegend=True,
                legend=dict(font=dict(color="#adbac7")),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Tarifa por tonelada
        st.markdown("---")
        st.markdown("### 🌾 Tarifa por Tonelada")
        tc1, tc2 = st.columns(2)
        toneladas = tc1.number_input("Toneladas a transportar", value=28, step=1)
        if toneladas > 0:
            tarifa_tn = total_sug / toneladas
            tc2.metric("💲 Tarifa por Tonelada", f"${tarifa_tn:,.0f}/tn")

    elif o_c != "TODAS" and d_c != "TODAS":
        st.warning("⚠️ No se pudo calcular la distancia para ese par de ciudades.")
    else:
        st.info("Seleccioná origen y destino para calcular.")

# ─── TAB 5: ESTADÍSTICAS ────────────────────────────────────
with tab5:
    st.subheader("📈 Panel de Estadísticas")

    if df_ca_raw.empty and df_ch_raw.empty:
        empty_state("No hay datos disponibles para mostrar estadísticas.")
    else:
        # Métricas generales
        total_cargas   = len(df_ca_raw) if not df_ca_raw.empty else 0
        total_camiones = len(df_ch_raw) if not df_ch_raw.empty else 0
        activas_ca     = sum(1 for _, r in df_ca_raw.iterrows() if not esta_expirada(r.iloc[0])) if not df_ca_raw.empty else 0
        activos_ch     = sum(1 for _, r in df_ch_raw.iterrows() if not esta_expirada(r.iloc[0])) if not df_ch_raw.empty else 0

        e1, e2, e3, e4 = st.columns(4)
        e1.metric("🏢 Cargas Activas",   activas_ca,     f"de {total_cargas} totales")
        e2.metric("🚛 Camiones Activos", activos_ch,     f"de {total_camiones} totales")
        e3.metric("📊 Relación C/C",
                  f"{activas_ca}/{activos_ch}" if activos_ch else "N/D",
                  "cargas por camión")
        demanda = "✅ Balanceado"
        if activos_ch > 0 and activas_ca / activos_ch > 1.5:
            demanda = "⚠️ + Cargas que Camiones"
        elif activos_ch > 0 and activas_ca / activos_ch < 0.6:
            demanda = "⚠️ + Camiones que Cargas"
        e4.metric("📡 Estado Mercado", demanda)

        st.markdown("---")
        col_g1, col_g2 = st.columns(2)

        # Rutas más frecuentes (Cargas)
        if not df_ca_raw.empty:
            with col_g1:
                st.markdown("#### 🏆 Rutas más publicadas (Cargas)")
                try:
                    df_rutas = df_ca_raw.copy()
                    df_rutas["ruta"] = df_rutas.iloc[:, 1].astype(str) + " → " + df_rutas.iloc[:, 2].astype(str)
                    top_rutas = df_rutas["ruta"].value_counts().head(8).reset_index()
                    top_rutas.columns = ["Ruta", "Publicaciones"]
                    fig_bar = px.bar(
                        top_rutas, x="Publicaciones", y="Ruta", orientation="h",
                        color="Publicaciones",
                        color_continuous_scale=["#1c2128", "#539bf5"],
                    )
                    fig_bar.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#adbac7", margin=dict(t=10, b=10, l=10, r=10),
                        yaxis=dict(tickfont=dict(size=10)),
                        coloraxis_showscale=False,
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                except Exception as ex:
                    st.warning(f"No se pudieron graficar rutas: {ex}")

        # Actividad por hora
        if not df_ca_raw.empty:
            with col_g2:
                st.markdown("#### 🕐 Actividad por Hora del Día")
                try:
                    df_horas = df_ca_raw.copy()
                    df_horas["hora"] = pd.to_datetime(df_horas.iloc[:, 0], errors="coerce").dt.hour
                    df_horas = df_horas.dropna(subset=["hora"])
                    conteo_horas = df_horas["hora"].value_counts().sort_index().reset_index()
                    conteo_horas.columns = ["Hora", "Publicaciones"]
                    fig_line = px.line(
                        conteo_horas, x="Hora", y="Publicaciones",
                        markers=True, line_shape="spline",
                        color_discrete_sequence=["#539bf5"],
                    )
                    fig_line.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font_color="#adbac7", margin=dict(t=10, b=10, l=10, r=10),
                        xaxis=dict(tickmode="linear", dtick=2),
                    )
                    fig_line.update_traces(fill="tozeroy", fillcolor="rgba(83,155,245,0.1)")
                    st.plotly_chart(fig_line, use_container_width=True)
                except Exception as ex:
                    st.warning(f"No se pudo graficar actividad: {ex}")

        # Mercaderías más frecuentes
        if not df_ca_raw.empty:
            st.markdown("---")
            st.markdown("#### 📦 Mercaderías más frecuentes")
            try:
                df_merc = df_ca_raw[~df_ca_raw.iloc[:, 1].astype(str).str.contains("ARRIME", case=False)]
                top_merc = df_merc.iloc[:, 3].astype(str).str.upper().value_counts().head(6).reset_index()
                top_merc.columns = ["Mercadería", "Cantidad"]
                fig_merc = px.bar(
                    top_merc, x="Mercadería", y="Cantidad",
                    color="Cantidad", color_continuous_scale=["#1c2a1c", "#4caf50"],
                )
                fig_merc.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#adbac7", margin=dict(t=10, b=10, l=10, r=10),
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_merc, use_container_width=True)
            except Exception as ex:
                st.warning(f"No se pudo graficar mercaderías: {ex}")

        # Mapa de calor de ciudades de origen
        if not df_ca_raw.empty:
            st.markdown("---")
            st.markdown("#### 🗺️ Mapa de Ciudades de Origen")
            try:
                df_mapa = df_ca_raw.copy()
                df_mapa["ciudad"] = df_mapa.iloc[:, 1].astype(str).str.upper()
                conteo_ciudades = df_mapa["ciudad"].value_counts().reset_index()
                conteo_ciudades.columns = ["Ciudad", "Publicaciones"]

                lats, lons, nombres, cantidades = [], [], [], []
                for _, row in conteo_ciudades.iterrows():
                    ciudad_key = next((k for k in COORDS_CIUDADES if row["Ciudad"] in k), None)
                    if ciudad_key and ciudad_key != "TODAS":
                        lat, lon = COORDS_CIUDADES[ciudad_key]
                        lats.append(lat); lons.append(lon)
                        nombres.append(row["Ciudad"]); cantidades.append(row["Publicaciones"])

                if lats:
                    fig_map = go.Figure(go.Scattergeo(
                        lat=lats, lon=lons,
                        text=[f"{n}: {c} pub." for n, c in zip(nombres, cantidades)],
                        mode="markers",
                        marker=dict(
                            size=[min(8 + c * 4, 40) for c in cantidades],
                            color=cantidades,
                            colorscale="Blues",
                            showscale=True,
                            colorbar=dict(title="Publicaciones", tickfont=dict(color="#adbac7")),
                        ),
                    ))
                    fig_map.update_layout(
                        geo=dict(
                            scope="south america",
                            showland=True, landcolor="#1c2128",
                            showocean=True, oceancolor="#0e1117",
                            showcountries=True, countrycolor="#30363d",
                            showsubunits=True, subunitcolor="#30363d",
                            center=dict(lat=-32, lon=-62),
                            projection_scale=4,
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font_color="#adbac7",
                        margin=dict(t=10, b=10, l=0, r=0),
                        height=400,
                    )
                    st.plotly_chart(fig_map, use_container_width=True)
            except Exception as ex:
                st.warning(f"No se pudo generar el mapa: {ex}")

# ============================================================
# 13. FOOTER
# ============================================================
st.markdown(
    "<div style='text-align:center; padding:20px; opacity:0.5;'>"
    "<b>Creado por Ignacio Diaz - 2026</b><br>"
    "<small>Retorno Match VIP | Sistema de Coordinación de Cargas</small>"
    "</div>",
    unsafe_allow_html=True,
)
