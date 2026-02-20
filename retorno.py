import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

PROVINCIAS = ["CUALQUIERA", "BUENOS AIRES", "CABA", "CATAMARCA", "CHACO", "CHUBUT", "CORDOBA", "CORRIENTES", "ENTRE RIOS", "FORMOSA", "JUJUY", "LA PAMPA", "LA RIOJA", "MENDOZA", "MISIONES", "NEUQUEN", "RIO NEGRO", "SALTA", "SAN JUAN", "SAN LUIS", "SANTA CRUZ", "SANTA FE", "SANTIAGO DEL ESTERO", "TIERRA DEL FUEGO", "TUCUMAN"]
EQUIPOS = ["CUALQUIERA", "Chasis", "Semi", "Sider", "Batea", "Térmico", "Acoplado"]
TIPOS_CARGA = ["General", "Paletizado", "Granel", "Peligrosa", "Refrigerada"]

# --- 2. FUNCIONES DE LÓGICA LOGÍSTICA ---
def obtener_distancia(origen, destino):
    o, d = str(origen).upper(), str(destino).upper()
    km_data = {
        ("SAN JORGE", "ROSARIO"): 185, ("ROSARIO", "SAN JORGE"): 185,
        ("SAN JORGE", "SANTA FE"): 155, ("SANTA FE", "SAN JORGE"): 155,
        ("SAN JORGE", "CORDOBA"): 275, ("CORDOBA", "SAN JORGE"): 275,
        ("SAN JORGE", "BUENOS AIRES"): 480, ("BUENOS AIRES", "SAN JORGE"): 480
    }
    for (r_o, r_d), valor in km_data.items():
        if r_o in o and r_d in d: return valor
    return None

def validar_vencimiento(fecha_str):
    try:
        vence = pd.to_datetime(fecha_str).date()
        hoy = datetime.now().date()
        if vence < hoy: return "🔴 VENCIDO", False
        if vence <= hoy + timedelta(days=15): return "🟡 VENCE PRONTO", True
        return "🟢 DOCUMENTACIÓN AL DÍA", True
    except:
        return "⚪ SIN FECHA CARGADA", True

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 3. ESTILOS BLINDADOS ---
st.markdown("""
<style>
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .badge-vence { padding: 4px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; margin-bottom: 10px; display: inline-block; }
    .vence-ok { background: #eaffea; color: #155724; }
    .vence-warning { background: #fff3cd; color: #856404; }
    .vence-danger { background: #f8d7da; color: #721c24; }
    .footer { text-align: center; color: white; padding: 40px; font-size: 12px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    .legal-box { font-size: 10px; color: rgba(255,255,255,0.5); margin-top: 20px; line-height: 1.2; }
    .btn-wsp { background-color: #25D366; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- 4. DATA ---
try:
    df_ch_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").fillna("-")
    df_ca_raw = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").fillna("-")
except:
    df_ch_raw, df_ca_raw = pd.DataFrame(), pd.DataFrame()

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
            venc = st.date_input("Vencimiento de Seguro/RTO") # NUEVO FILTRO DE CONFIANZA
            if st.form_submit_button("PUBLICAR"):
                data = {"entry.1304806144": f"{o} ({lo})", "entry.1519265625": f"{d} ({ld})", "entry.597193898": e, "entry.1542650763": cu, "entry.769375120": doc, "entry.1574172378": w, "entry.999999999": str(venc)}
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("¡Publicado!"); st.rerun()

# --- PESTAÑA EMPRESA (Donde se ve la validación) ---
with t2:
    col_f2, col_r2 = st.columns([1, 2.2])
    with col_f2:
        st.markdown("<h4 style='color:white;'>🏢 Publicar Carga</h4>", unsafe_allow_html=True)
        # Formulario de carga (Mantiene estructura blindada)
        with st.form("form_empresa"):
            st.write("Complete los datos de la carga...")
            st.form_submit_button("SUBIR CARGA")
            
    with col_r2:
        if not df_ch_raw.empty:
            for _, r in df_ch_raw.iloc[::-1].iterrows():
                # Lógica de Validación de Confianza
                estado_doc, mostrar = validar_vencimiento(r[6] if len(r)>6 else "")
                cls = "vence-danger" if "🔴" in estado_doc else "vence-warning" if "🟡" in estado_doc else "vence-ok"
                
                if mostrar: # Solo muestra si no está vencido (o podés elegir mostrarlo igual con el cartel rojo)
                    st.markdown(f'''<div class="card-white">
                        <div class="badge-vence {cls}">{estado_doc}</div>
                        <div style="font-size:20px; font-weight:900; color:#1e3799;">{r[1]} ➔ {r[2]}</div>
                        <b>🚛 EQUIPO:</b> {r[3]} | 🆔 <b>CUIT:</b> {r[5]}<br>
                        <div style="display:flex; gap:10px; margin-top:10px;">
                            <a href="https://api.whatsapp.com/send?phone={r[4]}" class="btn-wsp" style="flex:2;">💬 CONTACTAR CHOFER</a>
                            <a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 VER PAPELES</a>
                        </div>
                    </div>''', unsafe_allow_html=True)

# --- 7. FOOTER & LEGALES (IGNACIO DIAZ) ---
st.markdown(f"""
<div class="footer">
    <p>Desarrollado por <b>Ignacio Diaz</b></p>
    <div class="legal-box">
        AVISO LEGAL: PROHIBIDA LA RÉPLICA TOTAL O PARCIAL. El desarrollador no se responsabiliza por acuerdos entre privados.
    </div>
</div>
""", unsafe_allow_html=True)
