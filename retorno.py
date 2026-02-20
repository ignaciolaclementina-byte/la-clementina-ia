import streamlit as st
import pandas as pd
import time
import requests
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

# --- 2. GESTIÓN DE ESTADO ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 EN VIVO: Creado por Ignacio Diaz y sus legales. Sistema VIP Activado."

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")

# --- 3. ESTILOS DE LA IMAGEN (DISEÑO OSCURO Y PROFESIONAL) ---
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075');
        background-size: cover; background-attachment: fixed;
    }
    .main-header { text-align: center; margin-bottom: 20px; }
    .radar-container {
        background: #e74c3c; color: white; padding: 10px; border-radius: 5px;
        margin-bottom: 20px; font-weight: bold; border: 1px solid #f1c40f;
    }
    .filter-bar {
        background: rgba(30, 39, 46, 0.9); padding: 15px; border-radius: 10px; margin-bottom: 20px;
    }
    .form-container {
        background: rgba(45, 52, 54, 0.8); padding: 20px; border-radius: 10px; border-left: 5px solid #f1c40f;
    }
    .card-res {
        background: white !important; border-radius: 10px; padding: 15px; margin-bottom: 15px;
        border-left: 10px solid #2ecc71; color: #333;
    }
    .card-vip {
        background: #fffdf0 !important; border: 2px solid #f1c40f !important;
        border-radius: 10px; padding: 15px; margin-bottom: 15px;
    }
    .route-header { font-size: 18px; font-weight: 800; color: #2c3e50; text-transform: uppercase; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 8px; border-radius: 5px;
        text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; width: 100%; text-align: center;
    }
    .footer { text-align: center; color: #7f8c8d; padding: 20px; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 4. ENCABEZADO ---
st.markdown('<div class="main-header"><img src="https://i.ibb.co/LhyYx7mY/logo-vip.png" width="180"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="radar-container"><marquee scrollamount="8">🔥 {st.session_state.anuncios}</marquee></div>', unsafe_allow_html=True)

# --- 5. FILTROS SUPERIORES ---
with st.container():
    st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
    with f2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
    with f3: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. FUNCIONES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

def es_vip(dato):
    lista = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista

# Carga de datos
try:
    df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch, df_ca = pd.DataFrame(), pd.DataFrame()

# --- 7. CUERPO PRINCIPAL (DOS COLUMNAS) ---
t1, t2 = st.tabs(["🚀 BUSCAR CAMIONES (SOY EMPRESA)", "🏢 BUSCAR CARGAS (SOY CHOFER)"])

with t1:
    col_izq, col_der = st.columns([1, 1.8])
    with col_izq:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📢 Publicar Carga")
        with st.form("f_carga", clear_on_submit=True):
            o = st.selectbox("Prov. Origen", PROVINCIAS[1:]); lo = st.text_input("Localidad Origen")
            d = st.selectbox("Prov. Destino", PROVINCIAS[1:]); ld = st.text_input("Localidad Destino")
            c = st.text_input("Carga (ej: Paletizado)"); n = st.text_input("Empresa"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407": f"{o} ({lo})", "entry.170847116": f"{d} ({ld})", "entry.576675281": c, "entry.1930562861": n, "entry.466540450": w})
                st.success("Carga subida!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_der:
        if not df_ch.empty:
            df_ch['vip'] = df_ch.iloc[:, 5].apply(es_vip)
            res = df_ch[df_ch.iloc[:,0].apply(es_hoy)].sort_values('vip', ascending=False)
            for _, r in res.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e == str(r[3])):
                    clase = "card-vip" if r['vip'] else "card-res"
                    label = "⭐ CHOFER VIP" if r['vip'] else "CAMIÓN DISPONIBLE"
                    st.markdown(f'''<div class="{clase}"><small style="color:#f39c12; font-weight:bold;">{label}</small>
                    <div class="route-header">{r[1]} ➔ {r[2]}</div>
                    <b>EQUIPO:</b> {r[3]} | <b>ID:</b> {r[5]}<br>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">💬 CONSULTAR</a></div>''', unsafe_allow_html=True)

with t2:
    col_izq2, col_der2 = st.columns([1, 1.8])
    with col_izq2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.subheader("📢 Publicar Camión")
        with st.form("f_camion", clear_on_submit=True):
            o2 = st.selectbox("Prov. Origen ", PROVINCIAS[1:]); lo2 = st.text_input("Loc. Origen")
            d2 = st.selectbox("Prov. Destino ", PROVINCIAS[1:]); ld2 = st.text_input("Loc. Destino")
            e2 = st.selectbox("Equipo ", EQUIPOS[1:]); cu2 = st.text_input("CUIT"); w2 = st.text_input("WhatsApp ")
            if st.form_submit_button("SUBIR CAMIÓN"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": f"{o2} ({lo2})", "entry.1519265625": f"{d2} ({ld2})", "entry.597193898": e2, "entry.1542650763": cu2, "entry.1574172378": w2})
                st.success("Camión subido!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_der2:
        if not df_ca.empty:
            df_ca['vip'] = df_ca.iloc[:, 5].apply(es_vip)
            res2 = df_ca[df_ca.iloc[:,0].apply(es_hoy)].sort_values('vip', ascending=False)
            for _, r in res2.iterrows():
                if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                    clase = "card-vip" if r['vip'] else "card-res"
                    label = "⭐ EMPRESA VIP" if r['vip'] else "CARGA DISPONIBLE"
                    st.markdown(f'''<div class="{clase}"><small style="color:#f39c12; font-weight:bold;">{label}</small>
                    <div class="route-header">{r[1]} ➔ {r[2]}</div>
                    <b>CARGA:</b> {r[3]} | <b>EMPRESA:</b> {r[5]}<br>
                    <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" class="btn-wsp">💬 CONSULTAR</a></div>''', unsafe_allow_html=True)

# --- PANEL DE CONTROL ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (ADMIN)"):
    st.session_state.anuncios = st.text_input("Mensaje Radar:", st.session_state.anuncios)
    st.session_state.socios_activos = st.text_area("Lista VIP:", st.session_state.socios_activos)
    if st.button("GUARDAR"): st.rerun()

st.markdown('<div class="footer">Creado por Ignacio Diaz y sus legales. 2026.</div>', unsafe_allow_html=True)
