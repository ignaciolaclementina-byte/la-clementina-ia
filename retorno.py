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

# --- 2. CARGA DE DATOS ROBUSTA ---
@st.cache_data(ttl=5)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        # Cargamos y forzamos que no haya errores por columnas faltantes
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        try:
            df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
            vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        except:
            vips_lista = []
            
        return df_ch, df_ca, vips_lista
    except Exception as e:
        st.error(f"Error de conexión con la base de datos: {e}")
        return pd.DataFrame(), pd.DataFrame(), []

# Inicializamos
df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()

# --- 3. FUNCIONES DE LIMPIEZA ---
def es_fecha(f, target):
    try:
        # Convertimos a string y chequeamos que no sea un guion
        f_str = str(f).strip()
        if f_str == "-" or len(f_str) < 5: return False
        return pd.to_datetime(f_str, dayfirst=True, errors='coerce').date() == target
    except:
        return False

def limpiar_wsp(num):
    s = "".join(filter(str.isdigit, str(num).replace(".0", "")))
    if not s: return "5491111111111"
    if s.startswith("0"): s = s[1:]
    if s.startswith("15"): s = s.replace("15", "", 1)
    return "549" + s if not s.startswith("549") else s

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 4. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# Estilos Pro-Mobile
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .radar-container { background: #e74c3c; color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; text-align: center; border: 1px solid #f1c40f; }
    .card-pro { background: #ffffff !important; border-radius: 15px; padding: 18px; margin-bottom: 12px; border-left: 8px solid #3498db; color: #1e1e1e; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .card-vip { background: #fff9e6 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 18px; margin-bottom: 12px; color: #1e1e1e; }
    .card-cosecha { background: #f1f8e9 !important; border-radius: 15px; padding: 18px; margin-bottom: 12px; border-left: 8px solid #2e7d32; color: #1b5e20; }
    .route-txt { font-size: 1.1rem; font-weight: 900; color: #1e3799; text-transform: uppercase; line-height: 1.2; }
    .val-pro { font-size: 1rem; font-weight: 700; color: #333; margin-top: 5px; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .label-pro { font-size: 10px; color: #7f8c8d; font-weight: bold; text-transform: uppercase; }
    @media (max-width: 600px) { .route-txt { font-size: 1rem !important; } }
</style>
""", unsafe_allow_html=True)

# --- 5. INTERFAZ ---
st.markdown("<h2 style='text-align:center;'>🚛 RETORNO MATCH VIP</h2>", unsafe_allow_html=True)

hoy = datetime.now().date()
c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN", ["CUALQUIERA"] + sorted(list(set(df_ch_raw.iloc[:,1].unique()) if not df_ch_raw.empty else [])))
with c2: b_d = st.selectbox("🏁 DESTINO", ["CUALQUIERA"] + sorted(list(set(df_ch_raw.iloc[:,2].unique()) if not df_ch_raw.empty else [])))
with c3: b_e = st.selectbox("🚛 EQUIPO", ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"])
with c4: b_f = st.date_input("📅 FECHA", hoy)

if 'anuncios' not in st.session_state: st.session_state.anuncios = "¡Bienvenido Ignacio Diaz!"
st.markdown(f'<div class="radar-container"><marquee>⭐ {st.session_state.anuncios} -- Por Ignacio Diaz</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "🌾 ARRIME"])

# --- LÓGICA DE FILTRADO SEGURA ---
with tab1:
    if not df_ch_raw.empty:
        # Filtrado por fecha y VIP
        df_ch_raw['is_vip'] = df_ch_raw.apply(lambda x: es_vip(x[4]) or es_vip(x[5]), axis=1)
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))].sort_values(by='is_vip', ascending=False)
        
        for _, r in df_f.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1])) and (b_d=="CUALQUIERA" or b_d in str(r[2])) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                w = limpiar_wsp(r[4] if len(str(r[4])) < 13 else r[5])
                link = f"https://api.whatsapp.com/send?phone={w}&text=Hola, vi tu camion {r[3]} en el sistema..."
                st.markdown(f'<div class="{"card-vip" if r["is_vip"] else "card-pro"}">{"⭐ VIP" if r["is_vip"] else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><div class="val-pro">🚛 {r[3]}</div><a href="{link}" target="_blank" class="btn-wsp">ENVIAR PROPUESTA</a></div>', unsafe_allow_html=True)

with tab2:
    if not df_ca_raw.empty:
        # Filtro: Excluir los arrimes para que no se dupliquen
        df_ca_f = df_ca_raw[~df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        df_f2 = df_ca_f[df_ca_f.iloc[:, 0].apply(lambda x: es_fecha(x, b_f))]
        
        for _, r in df_f2.iterrows():
            if (b_o=="CUALQUIERA" or b_o in str(r[1])) and (b_d=="CUALQUIERA" or b_d in str(r[2])):
                w = limpiar_wsp(r[4])
                link = f"https://api.whatsapp.com/send?phone={w}&text=Consulto por carga {r[3]}..."
                st.markdown(f'<div class="card-pro"><div class="route-txt">{r[1]} ➔ {r[2]}</div><div class="val-pro">📦 {r[3]}</div><div class="label-pro">Empresa: {r[5]}</div><a href="{link}" target="_blank" class="btn-wsp">CONSULTAR</a></div>', unsafe_allow_html=True)

with tab3:
    st.markdown("<h4 style='text-align:center; color:#f1c40f;'>🌾 OPERATIVOS DE ARRIME</h4>", unsafe_allow_html=True)
    if not df_ca_raw.empty:
        # Buscamos "ARRIME" en cualquier parte de la fila
        df_arr = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        
        for _, r in df_arr.iterrows():
            p = str(r[3]).split("|")
            det = p[1] if len(p) > 1 else r[3]
            tar = p[2] if len(p) > 2 else "A consultar"
            w = limpiar_wsp(r[4])
            link = f"https://api.whatsapp.com/send?phone={w}&text=Me interesa el arrime en {r[2]}..."
            st.markdown(f'''<div class="card-cosecha">
                <div class="route-txt" style="color:#2e7d32;">📍 {r[2]}</div>
                <div style="display:flex; justify-content:space-between; margin-top:8px;">
                    <div><div class="label-pro">DETALLE</div><div class="val-pro">{det}</div></div>
                    <div style="text-align:right;"><div class="label-pro">TARIFA</div><div class="val-pro" style="color:#2e7d32;">{tar}</div></div>
                </div>
                <a href="{link}" target="_blank" class="btn-wsp" style="background:#2e7d32;">🚜 POSTULAR</a>
            </div>''', unsafe_allow_html=True)

# --- PIE DE PÁGINA ---
st.markdown(f"<div style='text-align:center; padding:20px; font-size:12px; color:gray;'><b>Creado por Ignacio Diaz</b><br>© 2026 RETORNO MATCH VIP</div>", unsafe_allow_html=True)

with st.expander("⚙️"):
    if st.text_input("PIN", type="password") == ADMIN_PIN:
        st.session_state.anuncios = st.text_area("Radar", st.session_state.anuncios)
