import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import random

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS (LIMPIEZA VISUAL) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075');
        background-size: cover;
    }
    .card {
        background: white; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        border-left: 8px solid #3498db; color: #1e272e;
    }
    .card-urgente {
        background: #fffafa; border-radius: 12px; padding: 18px; margin-bottom: 12px;
        border-left: 8px solid #e74c3c; color: #1e272e;
    }
    .route-txt { font-size: 20px; font-weight: bold; color: #1e3799; margin-bottom: 5px; }
    .vistos { font-size: 12px; color: #7f8c8d; font-weight: bold; float: right; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 10px; 
        border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .footer { text-align: center; color: #bdc3c7; padding: 30px; font-size: 13px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 3. LOGICA ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if clean.startswith("0"): clean = clean[1:]
    return "549" + clean if not clean.startswith("549") else clean

# --- 4. BÚSQUEDA ---
c1, c2, c3 = st.columns([2, 2, 1])
with c1: b_origen = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c2: b_destino = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c3: 
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 REFRESCAR", use_container_width=True): st.rerun()

t1, t2 = st.tabs(["🚀 BUSCAR CARGAS", "🏢 BUSCAR CAMIONES"])

# --- PESTAÑA CARGAS ---
with t1:
    col_f, col_r = st.columns([1, 2])
    with col_f:
        st.markdown("<h4 style='color:white;'>Publicar mi Camión</h4>", unsafe_allow_html=True)
        with st.form("f1", clear_on_submit=True):
            o = st.selectbox("Origen", PROVINCIAS[1:]); d = st.selectbox("Destino", PROVINCIAS[1:])
            e = st.selectbox("Equipo", ["Chasis", "Semi", "Sider", "Batea", "Térmico"])
            w = st.text_input("WhatsApp"); cu = st.text_input("CUIT")
            if st.form_submit_button("PUBLICAR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e, "entry.1574172378": w, "entry.1542650763": cu})
                st.success("Publicado"); time.sleep(1); st.rerun()
    with col_r:
        try:
            df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").iloc[::-1]
            for _, r in df.head(15).iterrows():
                if (b_origen=="CUALQUIERA" or b_origen in str(r[1])) and (b_destino=="CUALQUIERA" or b_destino in str(r[2])):
                    urg = "🔥" in str(r[3])
                    clase = "card-urgente" if urg else "card"
                    v = random.randint(10, 50)
                    msg = urllib.parse.quote(f"Hola, vi tu carga {r[3]} en Retorno Match. ¿Sigue disponible?")
                    st.markdown(f'''<div class="{clase}"><span class="vistos">👁️ {v}</span>
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>Carga:</b> {r[3]} | <b>Empresa:</b> {r[5]}<br><b>Sale:</b> {r[6]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg}" class="btn-wsp">CONTACTAR CARGA</a></div>''', unsafe_allow_html=True)
        except: st.info("Cargando...")

# --- PESTAÑA CAMIONES ---
with t2:
    col_f2, col_r2 = st.columns([1, 2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>Publicar mi Carga</h4>", unsafe_allow_html=True)
        with st.form("f2", clear_on_submit=True):
            eo = st.selectbox("Origen", PROVINCIAS[1:]); ed = st.selectbox("Destino", PROVINCIAS[1:])
            ec = st.text_input("¿Qué cargás?"); urg_ch = st.checkbox("MARCAR COMO URGENTE")
            en = st.text_input("Tu Empresa"); ew = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                txt_c = f"🔥 {ec}" if urg_ch else ec
                requests.post(URL_CARGAS_POST, data={"entry.610070407": eo, "entry.170847116": ed, "entry.576675281": txt_c, "entry.1930562861": en, "entry.466540450": ew})
                st.success("Subida"); time.sleep(1); st.rerun()
    with col_r2:
        try:
            df2 = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").iloc[::-1]
            for _, r in df2.head(15).iterrows():
                if (b_origen=="CUALQUIERA" or b_origen in str(r[1])) and (b_destino=="CUALQUIERA" or b_destino in str(r[2])):
                    v2 = random.randint(5, 25)
                    msg2 = urllib.parse.quote(f"Hola, vi tu camion {r[3]} en Retorno Match. ¿Estas disponible?")
                    st.markdown(f'''<div class="card"><span class="vistos">👁️ {v2}</span>
                        <div class="route-txt">{r[1]} ➔ {r[2]}</div>
                        <b>Equipo:</b> {r[3]} | <b>CUIT:</b> {r[5]}
                        <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={msg2}" class="btn-wsp">CONTACTAR CHOFER</a></div>''', unsafe_allow_html=True)
        except: st.info("Cargando...")

st.markdown(f"""<div class="footer"><b>© 2026 RETORNO MATCH</b><br>Creado por Ignacio Diaz y sus legales</div>""", unsafe_allow_html=True)
