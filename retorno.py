import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import random

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS ORIGINALES BLINDADOS ---
st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important;
        background-size: cover !important; background-attachment: fixed !important;
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
        border-left: 10px solid #e74c3c; color: #333; position: relative; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .badge-vistos { 
        position: absolute; top: 15px; right: 20px; background: #f1c40f; 
        color: #2c3e50; padding: 2px 8px; border-radius: 5px; font-size: 12px; font-weight: bold;
    }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .btn-share {
        background-color: #3498db; color: white !important; padding: 8px; 
        border-radius: 8px; text-decoration: none; font-size: 12px; display: inline-block; margin-top: 5px;
    }
    .footer { text-align: center; color: white; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .legal { font-size: 10px; color: #bdc3c7; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 3. FUNCIONES ---
def limpiar_dato(val):
    return "".join(filter(str.isdigit, str(val)))

def limpiar_wsp(num):
    clean = limpiar_dato(num)
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

def es_hoy(f):
    try: return pd.to_datetime(f).date() == datetime.now().date()
    except: return False

# --- 4. BARRA DE BÚSQUEDA MEJORADA ---
c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
with c1: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
with c4:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 REFRESCAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

t1, t2 = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- PESTAÑA CHOFER ---
with t1:
    col_f1, col_r1 = st.columns([1, 2.2])
    with col_f1:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("form_chofer", clear_on_submit=True):
            o = st.selectbox("Provincia Origen", PROVINCIAS[1:]); lo = st.text_input("Localidad")
            d = st.selectbox("Provincia Destino", PROVINCIAS[1:]); ld = st.text_input("Localidad")
            e = st.selectbox("Equipo", EQUIPOS[1:])
            w = st.text_input("WhatsApp"); cu = st.text_input("CUIT (Solo números)")
            doc = st.text_input("Link Papeles (Drive/Dropbox)")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                cuit_limpio = limpiar_dato(cu)
                if len(cuit_limpio) < 11: st.error("CUIT incompleto")
                else:
                    data = {"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cuit_limpio, "entry.769375120": doc, "entry.1574172378": w}
                    requests.post(URL_CHOFERES_POST, data=data)
                    st.success("¡Camión publicado!"); time.sleep(1); st.rerun()
    with col_r1:
        try:
            df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
            for _, r in df_ca.iloc[::-1].iterrows():
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()):
                    # Nota: Aquí asumimos que en la columna de 'Carga' o similar se puede filtrar por equipo si se desea
                    urg = "🔥" in str(r[3])
                    v = random.randint(20, 80)
                    msg = urllib.parse.quote(f"Hola! Vi tu carga *{r[1]} -> {r[2]}* en Retorno Match. ¿Sigue disponible?")
                    share_msg = urllib.parse.quote(f"Ojo! Mirá esta carga en Retorno Match:\n📍 {r[1]} -> {r[2]}\n📦 {r[3]}\n🏢 {r[5]}")
                    
                    st.markdown(f'''<div class="{"card-urgent" if urg else "card-white"}">
                        <div class="badge-vistos">👁️ {v} interesados</div>
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}<br><b>⏳ SALE:</b> {r[6]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a>
                        <a href="https://api.whatsapp.com/send?text={share_msg}" target="_blank" class="btn-share">🔗 Compartir con colega</a>
                    </div>''', unsafe_allow_html=True)
        except: st.info("Buscando cargas...")

# --- PESTAÑA EMPRESA ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("form_empresa", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); elo = st.text_input("Loc. Origen")
            ed = st.selectbox("Destino", PROVINCIAS[1:]); eld = st.text_input("Loc. Destino")
            ec = st.text_input("Carga (Ej: 28tn Paletizado)"); u_ch = st.checkbox("🔥 MARCAR COMO URGENTE")
            en = st.text_input("Nombre Empresa"); ef = st.text_input("Fecha/Hora de carga"); ew = st.text_input("WhatsApp de contacto")
            if st.form_submit_button("SUBIR CARGA"):
                payload = {"entry.610070407": f"{eo} ({elo})", "entry.170847116": f"{ed} ({eld})", "entry.576675281": f"🔥 {ec}" if u_ch else ec, "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew}
                requests.post(URL_CARGAS_POST, data=payload)
                st.success("¡Carga publicada!"); time.sleep(1); st.rerun()
    with col_r2:
        try:
            df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
            for _, r in df_ch.iloc[::-1].iterrows():
                # Aplicamos filtro de equipo aquí
                if es_hoy(r[0]) and (b_o == "CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d == "CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e == "CUALQUIERA" or b_e == str(r[3])):
                    v_h = random.randint(10, 45)
                    msg_h = urllib.parse.quote(f"Hola! Vi tu camión *{r[3]}* en Retorno Match. ¿Estás disponible para una carga?")
                    st.markdown(f'''<div class="card-white">
                        <div class="badge-vistos">👁️ {v_h} vistas</div>
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}
                        <div style="display:flex;gap:10px;">
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg_h}" target="_blank" class="btn-wsp" style="flex:2;">💬 CONTACTAR</a>
                            <a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 PAPELES</a>
                        </div>
                    </div>''', unsafe_allow_html=True)
        except: st.info("Buscando camiones...")

# --- FOOTER ---
st.markdown(f"""
<div class="footer">
    <p><b>© 2026 RETORNO MATCH - San Jorge, Santa Fe</b></p>
    <p>Creado por <b>Ignacio Diaz y sus legales</b></p>
    <p class="legal">Aviso: Prohibida la reproducción total o parcial de esta interfaz.</p>
</div>
""", unsafe_allow_html=True)
