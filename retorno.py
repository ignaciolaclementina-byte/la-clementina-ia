import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ Y SUS LEGALES) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "ACA_PONES_EL_GID_VIP" # <-- Asegurate de tener este GID

# Google Form para automatizar la carga de VIPs desde la App (Opcional, pero recomendado)
# Si no tenés un Form para esto, el botón del panel te llevará directo a tu Excel.
ADMIN_PIN = "1323" 

# --- 2. CARGA DE DATOS ---
@st.cache_data(ttl=10)
def cargar_todo():
    try:
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
        # Leemos la lista VIP global desde el Excel
        try:
            df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}", header=None)
            vips = [str(x).strip().upper() for x in df_v[0].dropna().tolist()]
        except: vips = ["FLEMING"]
        return df_ch, df_ca, list(set(vips))
    except:
        return pd.DataFrame(), pd.DataFrame(), ["FLEMING"]

df_ch, df_ca, LISTA_VIPS = cargar_todo()

# --- 3. ESTILOS VIP ---
st.set_page_config(page_title="RETORNO MATCH VIP", layout="wide")
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; text-align: center; border: 1px solid #f1c40f; }
    .card-white { background: white; border-radius: 15px; padding: 20px; margin-bottom: 15px; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6; border: 4px solid #f1c40f; border-radius: 15px; padding: 20px; margin-bottom: 15px; color: #333; box-shadow: 0px 4px 20px rgba(241,196,15,0.6); }
    .vip-label { background: #f1c40f; color: black; padding: 4px 12px; border-radius: 20px; font-weight: 900; font-size: 14px; display: inline-block; margin-bottom: 10px; }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: white; padding: 30px; font-size: 14px; border-top: 1px solid rgba(255,255,255,0.2); margin-top: 40px; }
</style>
""", unsafe_allow_html=True)

# --- 4. BUSCADOR ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([1.5, 1.5, 1.5, 1.5, 1])
with c1: b_f = st.date_input("📅 FECHA:", datetime.now().date())
with c2: b_o = st.selectbox("🔍 ORIGEN:", ["CUALQUIERA", "BUENOS AIRES", "CABA", "CORDOBA", "SANTA FE", "MENDOZA", "ENTRE RIOS", "TUCUMAN", "SALTA", "CORRIENTES", "CHACO", "MISIONES", "SAN LUIS", "SAN JUAN", "LA RIOJA", "CATAMARCA", "JUJUY", "SANTIAGO DEL ESTERO", "FORMOSA", "NEUQUEN", "RIO NEGRO", "CHUBUT", "SANTA CRUZ", "TIERRA DEL FUEGO", "LA PAMPA"])
with c3: b_d = st.selectbox("🏁 DESTINO:", ["CUALQUIERA", "BUENOS AIRES", "CABA", "CORDOBA", "SANTA FE", "MENDOZA", "ENTRE RIOS", "TUCUMAN", "SALTA", "CORRIENTES", "CHACO", "MISIONES", "SAN LUIS", "SAN JUAN", "LA RIOJA", "CATAMARCA", "JUJUY", "SANTIAGO DEL ESTERO", "FORMOSA", "NEUQUEN", "RIO NEGRO", "CHUBUT", "SANTA CRUZ", "TIERRA DEL FUEGO", "LA PAMPA"])
with c4: b_e = st.selectbox("🚛 EQUIPO:", ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"])
with c5:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR"): st.cache_data.clear(); st.rerun()

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">⭐ Membresías VIP Activas: Gestión Directa por Ignacio Diaz -- Creado por Ignacio Diaz y sus legales.</marquee></div>', unsafe_allow_html=True)

t1, t2 = st.tabs(["🚀 CAMIONES", "🏢 CARGAS"])

def limpiar_wsp(n):
    c = "".join(filter(str.isdigit, str(n)))
    return "549" + (c[1:] if c.startswith("0") else c) if not c.startswith("549") else c

# --- TAB 1: CAMIONES ---
with t1:
    col_f, col_r = st.columns([1, 2.2])
    with col_f:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        with st.form("f1"):
            o = st.text_input("Origen"); d = st.text_input("Destino"); c = st.text_input("Carga"); e = st.text_input("Empresa"); w = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":o,"entry.170847116":d,"entry.576675281":c,"entry.1930562861":e,"entry.466540450":w})
                st.success("Listo"); time.sleep(1); st.cache_data.clear(); st.rerun()
    with col_r:
        for _, r in df_ch.iterrows():
            try:
                if pd.to_datetime(r[0], dayfirst=True).date() == b_f:
                    if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()) and (b_e=="CUALQUIERA" or b_e==str(r[3])):
                        is_v = any(v in str(r[4]).upper() for v in LISTA_VIPS)
                        st.markdown(f'<div class="{"card-vip" if is_v else "card-white"}">{"<div class=\"vip-label\">⭐ CHOFER VIP</div>" if is_v else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>🚛:</b> {r[3]} | 🆔: {r[4]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Hola!" target="_blank" class="btn-wsp">💬 CONTACTAR</a></div>', unsafe_allow_html=True)
            except: continue

# --- TAB 2: CARGAS ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>📢 Publicar Camión</h4>", unsafe_allow_html=True)
        with st.form("f2"):
            o2 = st.text_input("Origen"); d2 = st.text_input("Destino"); e2 = st.selectbox("Equipo", ["Chasis", "Semi", "Sider", "Batea"]); cu = st.text_input("CUIT/ID"); w2 = st.text_input("WhatsApp")
            if st.form_submit_button("SUBIR"):
                requests.post(URL_CHOFERES_POST, data={"entry.1304806144":o2,"entry.1519265625":d2,"entry.597193898":e2,"entry.1542650763":cu,"entry.1574172378":w2})
                st.success("Listo"); time.sleep(1); st.cache_data.clear(); st.rerun()
    with col_r2:
        for _, r in df_ca.iterrows():
            try:
                if pd.to_datetime(r[0], dayfirst=True).date() == b_f:
                    if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (b_d=="CUALQUIERA" or b_d in str(r[2]).upper()):
                        is_v = any(v in str(r[4]).upper() for v in LISTA_VIPS)
                        st.markdown(f'<div class="{"card-vip" if is_v else "card-white"}">{"<div class=\"vip-label\">⭐ EMPRESA VIP</div>" if is_v else ""}<div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦:</b> {r[3]} | 🏢: {r[4]}<br><a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[5])}&text=Hola!" target="_blank" class="btn-wsp">💬 CONSULTAR</a></div>', unsafe_allow_html=True)
            except: continue

# --- 5. PANEL DE CONTROL EXCLUSIVO ---
st.markdown("---")
with st.expander("⚙️ GESTIÓN DE MEMBRESÍAS (IGNACIO DIAZ)"):
    if st.text_input("PIN de Acceso:", type="password") == ADMIN_PIN:
        st.info("Para dar de alta un VIP global, agrégalo a la lista en tu Excel.")
        # Link directo a la pestaña VIP para que no tengas que buscarla
        url_directa_vip = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_VIP}"
        st.markdown(f"""
            <a href="{url_directa_vip}" target="_blank" style="background-color: #f1c40f; color: black; padding: 15px; text-decoration: none; border-radius: 10px; font-weight: bold; display: block; text-align: center;">
                ➕ ABRIR GESTOR DE VIPS (EXCEL DIRECTO)
            </a>
        """, unsafe_allow_html=True)
        st.write("Solo escribe el nombre en la lista y cierra. ¡Se actualiza solo!")

st.markdown(f'<div class="legal-footer"><b>Creado por Ignacio Diaz y sus legales</b><br>© 2026 RETORNO MATCH VIP</div>', unsafe_allow_html=True)
