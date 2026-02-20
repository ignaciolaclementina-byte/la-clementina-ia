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

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]
TIPOS_CARGA = ["General", "Paletizado", "Granel", "Peligrosa", "Refrigerada"]

# --- 2. BASE DE DISTANCIAS REALES ---
def obtener_distancia(origen, destino):
    o, d = str(origen).upper(), str(destino).upper()
    km_data = {
        ("SAN JORGE", "ROSARIO"): 185, ("ROSARIO", "SAN JORGE"): 185,
        ("SAN JORGE", "SANTA FE"): 155, ("SANTA FE", "SAN JORGE"): 155,
        ("SAN JORGE", "CORDOBA"): 275, ("CORDOBA", "SAN JORGE"): 275,
        ("SAN JORGE", "BUENOS AIRES"): 480, ("BUENOS AIRES", "SAN JORGE"): 480,
        ("SANTA FE", "BUENOS AIRES"): 450, ("BUENOS AIRES", "SANTA FE"): 450,
        ("ROSARIO", "BUENOS AIRES"): 300, ("BUENOS AIRES", "ROSARIO"): 300,
        ("SANTA FE", "CORDOBA"): 350, ("CORDOBA", "SANTA FE"): 350,
        ("SANTA FE", "ROSARIO"): 170, ("ROSARIO", "SANTA FE"): 170
    }
    for (r_o, r_d), valor in km_data.items():
        if r_o in o and r_d in d: return valor
    return None

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
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; margin: 5px; border: 1px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; position: relative; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .card-urgent {
        background: #fff5f5 !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #e74c3c; color: #333;
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .badge-dist { background: #f1c40f; color: #2c3e50; padding: 4px 8px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 10px; border: 1px solid #2c3e50; }
    .footer { text-align: center; color: white; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .btn-share { background-color: #3498db; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 15px; border: 1px solid white; }
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

try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
    count_ch = len([x for x in df_ch_raw.iloc[:,0] if es_hoy(x)])
    count_ca = len([x for x in df_ca_raw.iloc[:,0] if es_hoy(x)])
except:
    df_ch_raw, df_ca_raw, count_ch, count_ca = pd.DataFrame(), pd.DataFrame(), 0, 0

# --- 5. RADAR ---
st.markdown(f"""
<div class="radar-container">
    <marquee scrollamount="8">
        🔥 EN VIVO: {count_ch} camiones y {count_ca} cargas hoy -- ⚠️ Nuevas publicaciones desde Rosario y San Jorge -- 🚛 Creado por Ignacio Diaz y sus legales.
    </marquee>
</div>
""", unsafe_allow_html=True)

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

# --- PESTAÑA CHOFER ---
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
                    km = obtener_distancia(r[1], r[2])
                    
                    # --- MENSAJE NIVEL PRO ---
                    msg_cargas = urllib.parse.quote(
                        f"─── 🚛 *RETORNO MATCH* ───\n"
                        f"📌 *NUEVA SOLICITUD DE CARGA*\n\n"
                        f"📍 *ORIGEN:* {r[1]}\n"
                        f"🏁 *DESTINO:* {r[2]}\n"
                        f"📦 *MERCADERÍA:* {r[3]}\n"
                        f"🏢 *EMPRESA:* {r[5]}\n"
                        f"📑 *TIPO:* {r[6]}\n"
                        f"{f'🛣️ *DISTANCIA:* {km} KM' if km else ''}\n\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *¿Sigue disponible? Me interesa el viaje.*"
                    )
                    
                    st.markdown(f'''<div class="{"card-urgent" if urg else "card-white"}">
                        <div class="route-txt">{r[1]} ➔ {r[2]} {f'<span class="badge-dist"> {km} KM </span>' if km else ''}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br>
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_cargas}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a>
                    </div>''', unsafe_allow_html=True)

# --- PESTAÑA EMPRESA ---
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
                    km_h = obtener_distancia(r[1], r[2])
                    
                    # --- MENSAJE NIVEL PRO ---
                    msg_camiones = urllib.parse.quote(
                        f"─── 🚛 *RETORNO MATCH* ───\n"
                        f"📌 *UNIDAD DISPONIBLE ENCONTRADA*\n\n"
                        f"📍 *TRAYECTO:* {r[1]} ➔ {r[2]}\n"
                        f"🚚 *EQUIPO:* {r[3]}\n"
                        f"🆔 *CUIT:* {r[5]}\n"
                        f"{f'🛣️ *DISTANCIA:* {km_h} KM' if km_h else ''}\n\n"
                        f"🔗 *DOCUMENTACIÓN:* {r[7]}\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"✅ *¿Estás disponible? Tengo una carga para tu unidad.*"
                    )
                    
                    st.markdown(f'''<div class="card-white">
                        <div class="route-txt">{r[1]} ➔ {r[2]} {f'<span class="badge-dist"> {km_h} KM </span>' if km_h else ''}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}
                        <div style="display:flex;gap:10px;">
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_camiones}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONTACTAR</a>
                            <a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 PAPELES</a>
                        </div>
                    </div>''', unsafe_allow_html=True)

# --- 7. FOOTER ---
url_oficial = "https://retorno-match-sanjorge.streamlit.app/"
share_msg = urllib.parse.quote(
    f"━━━━━━━━━━━━━━━━━━\n"
    f"🚛 *RETORNO MATCH - LOGÍSTICA EN VIVO*\n"
    f"━━━━━━━━━━━━━━━━━━\n\n"
    f"✅ *Conseguí cargas y retornos al instante.*\n"
    f"📍 *Ubicación:* San Jorge, Santa Fe.\n\n"
    f"🔗 *INGRESAR AQUÍ:* {url_oficial}\n\n"
    f"📌 _Plataforma creada por Ignacio Diaz_"
)

st.markdown(f"""
<div class="footer">
    <p><b>© 2026 RETORNO MATCH - San Jorge, Santa Fe</b></p>
    <p>Creado por <b>Ignacio Diaz y sus legales</b></p>
    <a href="https://api.whatsapp.com/send?text={share_msg}" target="_blank" class="btn-share">📲 RECOMENDAR APP POR WHATSAPP</a>
</div>
""", unsafe_allow_html=True)
