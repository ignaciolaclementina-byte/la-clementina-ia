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

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

# --- 2. GESTIÓN DE ESTADO OPTIMIZADA ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 Verificá tu unidad para aparecer primero -- Creado por Ignacio Diaz"

if 'socios_activos' not in st.session_state:
    # Ahora lo guardamos como un set para que sea ultra rápido el match
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 3. ESTILOS BLINDADOS (NO SE TOCAN) ---
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
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; position: relative;
    }
    .card-urgent {
        background: #fff5f5 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #e74c3c; color: #333;
    }
    .card-premium {
        background: #fffcf0 !important; border: 2.5px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #f1c40f !important; color: #333; box-shadow: 0px 4px 15px rgba(241, 196, 15, 0.4);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .footer { text-align: center; color: white; padding: 40px; font-size: 12px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 70px !important; background-color: #2c3e50 !important; color: white !important; font-size: 18px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 4. MOTOR DE VERIFICACIÓN ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

def es_verificado(dato):
    # Proceso ultra rápido: limpia y compara en mayúsculas
    lista = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista

url_app = "https://retorno-match-sanjorge.streamlit.app/"

# Carga de datos
try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
    count_ch = len([x for x in df_ch_raw.iloc[:,0] if es_hoy(x)])
    count_ca = len([x for x in df_ca_raw.iloc[:,0] if es_hoy(x)])
except:
    df_ch_raw, df_ca_raw, count_ch, count_ca = pd.DataFrame(), pd.DataFrame(), 0, 0

# --- 5. RADAR ---
st.markdown(f"""<div class="radar-container"><marquee scrollamount="8">🔥 EN VIVO: {count_ch} camiones y {count_ca} cargas hoy -- {st.session_state.anuncios} -- 🚛 Creado por Ignacio Diaz.</marquee></div>""", unsafe_allow_html=True)

# --- 6. BÚSQUEDA ---
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN:", ["CUALQUIERA"] + sorted(list(set(df_ca_raw.iloc[:,1].tolist() + df_ch_raw.iloc[:,1].tolist()))))
with c2: b_d = st.selectbox("🏁 DESTINO:", ["CUALQUIERA"] + sorted(list(set(df_ca_raw.iloc[:,2].tolist() + df_ch_raw.iloc[:,2].tolist()))))
with c3: b_e = st.selectbox("🚛 EQUIPO:", ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"])
with c4:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_chofer", clear_on_submit=True):
            o = st.text_input("Provincia/Loc Origen"); d = st.text_input("Provincia/Loc Destino")
            e = st.selectbox("Equipo", ["Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"])
            w = st.text_input("WhatsApp (Sin 0 ni 15)"); cu = st.text_input("CUIT (Solo números)")
            doc = st.text_input("Link Documentación (Opcional)")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144":o, "entry.1519265625":d, "entry.597193898":e, "entry.1542650763":cu, "entry.769375120":doc, "entry.1574172378":w})
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ca_raw.empty:
            for _, r in df_ca_raw.iloc[::-1].iterrows():
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1])) and (b_d == "CUALQUIERA" or b_d in str(r[2])):
                    es_prem = es_verificado(r[5])
                    tag = " ✅ <span style='color:#3498db; font-size:14px;'>EMPRESA VERIFICADA</span>" if es_prem else ""
                    st.markdown(f'''<div class="{"card-premium" if es_prem else ("card-urgent" if "🔥" in str(r[3]) else "card-white")}">
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}{tag}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">💬 CONSULTAR AHORA</a>
                    </div>''', unsafe_allow_html=True)

with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_empresa", clear_on_submit=True):
            eo = st.text_input("Origen"); ed = st.text_input("Destino")
            ec = st.text_input("¿Qué carga?"); u_ch = st.checkbox("🔥 URGENTE")
            en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":eo, "entry.170847116":ed, "entry.576675281":f"🔥 {ec}" if u_ch else ec, "entry.1930562861":en, "entry.466540450":ew})
                st.success("¡Subida!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iloc[::-1].iterrows():
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1])) and (b_d == "CUALQUIERA" or b_d in str(r[2])) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    es_prem = es_verificado(r[5]) # CUIT
                    tag_p = " ⭐ <span style='color:#f1c40f; font-size:14px;'>CHOFER PREMIUM</span>" if es_prem else ""
                    st.markdown(f'''<div class="{"card-premium" if es_prem else "card-white"}">
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}{tag_p}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp">💬 CONTACTAR CHOFER</a>
                    </div>''', unsafe_allow_html=True)

# --- 7. PANEL DE CONTROL (OPTIMIZADO IGNACIO) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (ADMINISTRACIÓN RÁPIDA)"):
    col_adm1, col_adm2 = st.columns(2)
    with col_adm1:
        st.info("📢 Anuncios del Radar")
        an_txt = st.text_area("Separar con '--'", st.session_state.anuncios, height=150)
    with col_adm2:
        cant_socios = len([s for s in st.session_state.socios_activos.split(",") if s.strip()])
        st.success(f"🏅 Socios Activos: {cant_socios}")
        soc_txt = st.text_area("CUITs o Empresas (Separar con COMA)", st.session_state.socios_activos, height=150)
    
    if st.button("🚀 APLICAR CAMBIOS EN TODA LA APP", use_container_width=True):
        st.session_state.anuncios = an_txt
        st.session_state.socios_activos = soc_txt
        st.rerun()

# --- 8. FOOTER ---
st.markdown(f"""<div class="footer"><p>Desarrollado por <b>Ignacio Diaz</b></p><div style="font-size: 10px; color: rgba(255,255,255,0.5);">AVISO LEGAL: PROHIBIDA LA RÉPLICA TOTAL O PARCIAL. Creado por Ignacio Diaz y sus legales.</div></div>""", unsafe_allow_html=True)
