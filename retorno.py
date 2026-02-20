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

# --- 2. GESTIÓN DE ESTADO (MEMORIA DE LA APP) ---
if 'anuncios' not in st.session_state:
    st.session_state.anuncios = "📢 ¡NUEVO! Verificá tu unidad o empresa para aparecer primero -- Consultas aquí -- 🚛 Creado por Ignacio Diaz"

if 'socios_activos' not in st.session_state:
    st.session_state.socios_activos = "20334445551, TRANSPORTES SAN JORGE, LOGISTICA DIAZ"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]
TIPOS_CARGA = ["General", "Paletizado", "Granel", "Peligrosa", "Refrigerada"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 3. ESTILOS ORIGINALES BLINDADOS ---
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
        background: #fffcf0 !important; border: 2px solid #f1c40f !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #f1c40f !important; color: #333; box-shadow: 0px 0px 15px rgba(241, 196, 15, 0.3);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .footer { text-align: center; color: white; padding: 40px; font-size: 12px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .stTabs [data-baseweb="tab"] { flex: 1; height: 70px !important; background-color: #2c3e50 !important; color: white !important; font-size: 18px !important; font-weight: 900 !important; }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 4. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

def es_verificado(dato):
    lista_socios = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
    return str(dato).strip().upper() in lista_socios

url_app = "https://retorno-match-sanjorge.streamlit.app/"

try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
    count_ch = len([x for x in df_ch_raw.iloc[:,0] if es_hoy(x)])
    count_ca = len([x for x in df_ca_raw.iloc[:,0] if es_hoy(x)])
except:
    df_ch_raw, df_ca_raw, count_ch, count_ca = pd.DataFrame(), pd.DataFrame(), 0, 0

# --- 5. RADAR DINÁMICO ---
st.markdown(f"""<div class="radar-container"><marquee scrollamount="8">🔥 EN VIVO: {count_ch} camiones y {count_ca} cargas hoy -- {st.session_state.anuncios} -- 🚛 Creado por Ignacio Diaz.</marquee></div>""", unsafe_allow_html=True)

# --- 6. BÚSQUEDA ---
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
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
            o = st.selectbox("Provincia Origen", PROVINCIAS[1:]); lo = st.text_input("Localidad Origen")
            d = st.selectbox("Provincia Destino", PROVINCIAS[1:]); ld = st.text_input("Localidad Destino")
            e = st.selectbox("Equipo", EQUIPOS[1:]); w = st.text_input("WhatsApp")
            cu = st.text_input("CUIT"); doc = st.text_input("Link Papeles")
            if st.form_submit_button("PUBLICAR"):
                data = {"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cu, "entry.769375120": doc, "entry.1574172378": w}
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("¡Publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        if not df_ca_raw.empty:
            for _, r in df_ca_raw.iloc[::-1].iterrows():
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    urg = "🔥" in str(r[3])
                    es_premium = es_verificado(r[5]) 
                    tag = " ✅ <span style='color:#3498db; font-size:14px;'>EMPRESA VERIFICADA</span>" if es_premium else ""
                    msg_share = urllib.parse.quote(f"─── 🚛 *RETORNO MATCH* ───\n📌 *CARGA DISPONIBLE*\n📍 *RUTA:* {r[1]} -> {r[2]}\n📦 *CARGA:* {r[3]}\n🔗 *VER EN APP:* {url_app}")
                    st.markdown(f'''<div class="{"card-premium" if es_premium else ("card-urgent" if urg else "card-white")}">
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}{tag}<br>
                        <div style="display:flex; gap:10px;">
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONSULTAR</a>
                            <a href="https://api.whatsapp.com/send?text={msg_share}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📲 COMPARTIR</a>
                        </div>
                    </div>''', unsafe_allow_html=True)

with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_empresa", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Carga"); u_ch = st.checkbox("🔥 MARCAR URGENTE")
            tm = st.selectbox("Tipo de Mercadería", TIPOS_CARGA)
            en = st.text_input("Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                payload = {"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": f"🔥 {ec}" if u_ch else ec, "entry.1930562861": en, "entry.1064058502": tm, "entry.466540450": ew}
                requests.post(URL_CARGAS_POST, data=payload)
                st.success("¡Subida!"); time.sleep(1); st.rerun()
    with col_r2:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iloc[::-1].iterrows():
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    es_prem = es_verificado(r[5]) 
                    tag_p = " ⭐ <span style='color:#f1c40f; font-size:14px;'>CHOFER PREMIUM</span>" if es_prem else ""
                    msg_share_ch = urllib.parse.quote(f"─── 🚛 *RETORNO MATCH* ───\n📌 *UNIDAD DISPONIBLE*\n📍 *RUTA:* {r[1]} -> {r[2]}\n🚚 *EQUIPO:* {r[3]}\n🔗 *VER EN APP:* {url_app}")
                    st.markdown(f'''<div class="{"card-premium" if es_prem else "card-white"}">
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}{tag_p}<br>
                        <div style="display:flex;gap:10px;">
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONTACTAR</a>
                            <a href="https://api.whatsapp.com/send?text={msg_share_ch}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📲 COMPARTIR</a>
                        </div>
                    </div>''', unsafe_allow_html=True)

# --- 7. PANEL DE CONTROL AVANZADO (ADMIN RÁPIDO) ---
st.markdown("---")
with st.expander("⚙️ PANEL DE CONTROL (ANUNCIOS Y MEMBRESÍAS)"):
    
    # NUEVA SECCIÓN: BAJA RÁPIDA
    st.subheader("❌ Baja de Socio (Quitar corona/verificado)")
    c_baja1, c_baja2 = st.columns([3, 1])
    socio_a_borrar = c_baja1.text_input("Ingrese CUIT o Nombre a eliminar de premium:")
    if c_baja2.button("BORRAR SOCIO", use_container_width=True):
        if socio_a_borrar:
            actuales = [s.strip().upper() for s in st.session_state.socios_activos.split(",") if s.strip()]
            objetivo = socio_a_borrar.strip().upper()
            if objetivo in actuales:
                actuales.remove(objetivo)
                st.session_state.socios_activos = ", ".join(actuales)
                st.success(f"✅ {objetivo} eliminado de premium.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("No se encontró ese socio.")
        else:
            st.warning("Escriba algo para borrar.")

    st.markdown("---")
    
    st.subheader("1. Gestión de Radar Publicitario")
    nuevo_anuncio = st.text_area("Texto del Radar:", st.session_state.anuncios)
    
    st.subheader("2. Gestión de Socios Premium (Lista Completa)")
    nuevos_socios = st.text_area("Lista de CUITs o Empresas (Separa con coma):", st.session_state.socios_activos)
    
    if st.button("🚀 GUARDAR TODO Y ACTUALIZAR APP"):
        st.session_state.anuncios = nuevo_anuncio
        st.session_state.socios_activos = nuevos_socios
        st.success("¡App actualizada!"); time.sleep(1); st.rerun()

# --- 8. FOOTER & LEGALES ---
st.markdown(f"""<div class="footer"><p>Desarrollado por <b>Ignacio Diaz</b></p><div style="font-size: 10px; color: rgba(255,255,255,0.5);">AVISO LEGAL: PROHIBIDA LA RÉPLICA TOTAL O PARCIAL. Creado por Ignacio Diaz y sus legales.</div></div>""", unsafe_allow_html=True)
