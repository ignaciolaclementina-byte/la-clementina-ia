import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
import math
from fpdf import FPDF # Librería necesaria para el PDF

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524" 

URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"

ADMIN_PIN = "1323" 
TIEMPO_EXCLUSIVO_MIN = 30  # Ventaja competitiva para usuarios VIP
WSP_VENTAS_VIP = "5493401525621" # Tu contacto para nuevos clientes VIP

COORDS_PROV = {
    "BUENOS AIRES": (-34.921, -57.954), "CABA": (-34.603, -58.381), "CATAMARCA": (-28.469, -65.785),
    "CHACO": (-27.451, -58.986), "CHUBUT": (-43.300, -65.102), "CORDOBA": (-31.413, -64.181),
    "CORRIENTES": (-27.469, -58.830), "ENTRE RIOS": (-31.733, -60.529), "FORMOSA": (-26.177, -58.178),
    "JUJUY": (-24.185, -65.299), "LA PAMPA": (-36.616, -64.283), "LA RIOJA": (-29.411, -66.850),
    "MENDOZA": (-32.889, -68.845), "MISIONES": (-27.367, -55.896), "NEUQUEN": (-38.951, -68.059),
    "RIO NEGRO": (-40.813, -62.996), "SALTA": (-24.785, -65.411), "SAN JUAN": (-31.537, -68.536),
    "SAN LUIS": (-33.295, -66.335), "SANTA CRUZ": (-51.622, -69.218), "SANTA FE": (-31.633, -60.700),
    "SANTIAGO DEL ESTERO": (-27.795, -64.263), "TIERRA DEL FUEGO": (-54.801, -68.303), "TUCUMAN": (-26.824, -65.222)
}

PROVINCIAS = ["CUALQUIERA"] + sorted(list(COORDS_PROV.keys()))
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]

# --- 2. SISTEMA ANTI-PAUSA ---
if "last_heartbeat" not in st.session_state:
    st.session_state.last_heartbeat = time.time()
if time.time() - st.session_state.last_heartbeat > 900:
    st.session_state.last_heartbeat = time.time()
    st.rerun()

# --- 3. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=10)
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        df_v = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_VIP}&header=None&t={t}", header=None)
        vips_lista = [str(x).strip().upper().replace(".0", "") for x in df_v[0].dropna().tolist()]
        return df_ch, df_ca, vips_lista
    except: return pd.DataFrame(), pd.DataFrame(), []

df_ch_raw, df_ca_raw, LISTA_VIPS_GLOBAL = cargar_datos_seguros()
ahora = datetime.now(); hoy = ahora.date()

# --- 4. FUNCIONES PDF Y AUXILIARES (LOGICA DE IGNACIO DIAZ) ---
def generar_manifiesto_pdf(tipo, origen, destino, detalle, contacto, empresa="Particular"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(30, 55, 153)
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "RETORNO MATCH VIP - MANIFIESTO", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, f"Documento oficial generado por el sistema de Ignacio Diaz", ln=True, align='C')
    pdf.cell(0, 10, f"Fecha: {ahora.strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"DETALLES DE LA OPERACIÓN: {tipo.upper()}", ln=True)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    pdf.set_font("Arial", size=12)
    datos = [("ORIGEN:", origen), ("DESTINO:", destino), ("DETALLE:", detalle), ("CONTACTO:", contacto), ("EMPRESA:", empresa)]
    for label, valor in datos:
        pdf.set_font("Arial", 'B', 11); pdf.cell(50, 8, label)
        pdf.set_font("Arial", size=11); pdf.cell(0, 8, str(valor), ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 9)
    pdf.multi_cell(0, 5, "Nota: Este documento es una constancia de contacto. Retorno Match VIP no se responsabiliza por las condiciones pactadas.")
    
    pdf.set_y(-30)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Creado por Ignacio Diaz - Prohibida su reproducción sin autorización", align='C', ln=True)
    return pdf.output(dest='S').encode('latin-1')

def calcular_distancia(o_str, d_str):
    try:
        o_clean = next((p for p in COORDS_PROV if p in o_str.upper()), None)
        d_clean = next((p for p in COORDS_PROV if p in d_str.upper()), None)
        if o_clean and d_clean:
            lat1, lon1 = COORDS_PROV[o_clean]; lat2, lon2 = COORDS_PROV[d_clean]
            a = math.sin(math.radians(lat2-lat1)/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
            return f"📍 {int(6371 * (2 * math.atan2(math.sqrt(a), math.sqrt(1-a))))} km aprox."
    except: pass
    return ""

def es_fecha(f, target):
    try: return pd.to_datetime(f, dayfirst=True, errors='coerce').date() == target
    except: return False

def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0","")))
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num).replace(".0","")))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

def es_vip(dato):
    return str(dato).strip().upper().replace(".0", "") in LISTA_VIPS_GLOBAL

# --- 5. ESTILOS CSS ---
st.set_page_config(page_title="RETORNO MATCH VIP", page_icon="⭐", layout="wide")
st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075'); background-size: cover; background-attachment: fixed; }
    .radar-container { background: rgba(231, 76, 60, 0.9); color: white; padding: 10px; border-radius: 10px; margin-bottom: 20px; font-weight: bold; text-align: center; border: 1px solid #f1c40f; }
    .card-white, .card-vip { border-radius: 15px; padding: 20px; margin-bottom: 15px; transition: 0.3s; background: white; border-left: 10px solid #3498db; color: #333; }
    .card-vip { background: #fff9e6; border: 3px solid #f1c40f; }
    .dist-badge { background: #34495e; color: #f1c40f; padding: 2px 8px; border-radius: 5px; font-size: 12px; float: right; font-weight: bold; }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 10px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
    .legal-footer { text-align: center; color: rgba(255,255,255,0.7); padding: 50px; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

# --- 6. INTERFAZ ---
st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH VIP</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔐 ACCESO")
    user_cuit = st.text_input("Ingresar CUIT:", "").strip()
    soy_vip_actual = es_vip(user_cuit)
    if soy_vip_actual: st.success("✅ VIP ACTIVO")

c1, c2, c3, c4 = st.columns(4)
with c1: b_fecha = st.date_input("📅 FECHA:", hoy)
with c2: b_o = st.selectbox("🔍 ORIGEN:", PROVINCIAS)
with c3: b_d = st.selectbox("🏁 DESTINO:", PROVINCIAS)
with c4: b_e = st.selectbox("🚛 EQUIPO:", EQUIPOS)
busqueda_libre = st.text_input("🔎 Búsqueda rápida (Empresa, Producto, Localidad...)", "").upper()

st.markdown(f'<div class="radar-container"><marquee scrollamount="8">Creado por Ignacio Diaz -- Cosecha Activa 2026 -- {st.session_state.get("anuncios","Conectando el transporte argentino")}</marquee></div>', unsafe_allow_html=True)

tab1, tab2, tab_adm = st.tabs(["🚀 CAMIONES", "🏢 CARGAS", "📊 ADMIN"])

# --- SECCION CAMIONES ---
with tab1:
    if not df_ch_raw.empty:
        df_ch_raw['vip'] = df_ch_raw.apply(lambda r: es_vip(r[4]) or es_vip(r[5]), axis=1)
        df_f = df_ch_raw[df_ch_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f.iterrows():
            dist = calcular_distancia(str(r[1]), str(r[2]))
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda_libre in str(r).upper()):
                wsp = r[4] if len(str(r[4])) < 11 else r[5]
                st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><span class="dist-badge">{dist}</span><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>EQUIPO:</b> {r[3]} | 📱 {ocultar_telefono(wsp)}</div>', unsafe_allow_html=True)
                pdf_bytes = generar_manifiesto_pdf("CAMIÓN DISPONIBLE", r[1], r[2], r[3], wsp)
                st.download_button(label="📄 Descargar Manifiesto", data=pdf_bytes, file_name=f"Manifiesto_{r[1]}.pdf", mime="application/pdf", key=f"ch_{_}")

# --- SECCION CARGAS ---
with tab2:
    if not df_ca_raw.empty:
        df_ca_raw['vip'] = df_ca_raw.iloc[:, 5].apply(es_vip)
        df_f2 = df_ca_raw[df_ca_raw.iloc[:, 0].apply(lambda x: es_fecha(x, b_fecha))].sort_values(by='vip', ascending=False)
        for _, r in df_f2.iterrows():
            dist = calcular_distancia(str(r[1]), str(r[2]))
            if (b_o=="CUALQUIERA" or b_o in str(r[1]).upper()) and (busqueda_libre in str(r).upper()):
                st.markdown(f'<div class="{"card-vip" if r["vip"] else "card-white"}"><span class="dist-badge">{dist}</span><div class="route-txt">{r[1]} ➔ {r[2]}</div><b>📦 CARGA:</b> {r[3]} | 🏢 {r[5]}</div>', unsafe_allow_html=True)
                pdf_bytes = generar_manifiesto_pdf("CARGA DISPONIBLE", r[1], r[2], r[3], r[4], r[5])
                st.download_button(label="📄 Descargar Ficha", data=pdf_bytes, file_name=f"Carga_{r[5]}.pdf", mime="application/pdf", key=f"ca_{_}")

# --- PANEL ADMIN CON DASHBOARD ---
with tab_adm:
    if st.text_input("PIN:", type="password") == ADMIN_PIN:
        st.markdown("### 📊 ESTADÍSTICAS DE HOY")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Camiones", len(df_ch_raw))
        col_m2.metric("Cargas", len(df_ca_raw))
        col_m3.metric("VIPs", len(LISTA_VIPS_GLOBAL))
        
        st.write("---")
        if not df_ca_raw.empty:
            st.write("📈 **Top Rutas Solicitadas**")
            st.bar_chart(df_ca_raw.iloc[:, 1].value_counts().head(5))
        
        if st.button("LIMPIAR CACHÉ"):
            st.cache_data.clear()
            st.rerun()

# --- PIE DE PÁGINA (BLINDADO - CREADO POR IGNACIO DIAZ) ---
st.markdown(f"""
<div class="legal-footer">
    <p style="font-size: 20px; font-weight: bold; color: white;">Creado por Ignacio Diaz</p>
    <p style="color: #f1c40f; font-weight: bold;">© 2026 RETORNO MATCH VIP</p>
    <p><b>Prohibida la copia total o parcial de esta interfaz sin autorización de Ignacio Diaz.</b></p>
</div>
""", unsafe_allow_html=True)
