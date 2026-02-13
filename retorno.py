import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS AVANZADO (Fondo + Tarjetas + Formulario)
st.markdown("""
    <style>
    /* FONDO DE PANTALLA FIJO */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                    url('https://images.unsplash.com/photo-1501700493788-fa1a4fc9fe62?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* DISEÑO DE TARJETAS */
    .camion-card {
        background: rgba(255, 255, 255, 1); /* Blanco sólido para máxima legibilidad */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border-left: 10px solid #25D366;
        transition: transform 0.2s;
    }
    .camion-card:hover {
        transform: scale(1.01);
    }

    /* TEXTOS INTERNOS */
    .route-text { font-size: 24px; font-weight: 900; color: #1a1a1a !important; margin: 0; }
    .detail-text { color: #555 !important; font-size: 16px; margin: 5px 0; }
    .fecha-text { color: #888 !important; font-size: 12px; }

    /* BOTÓN WHATSAPP */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 14px 28px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
    }
    .btn-wa:hover { background-color: #128C7E; }

    /* ESTILO DEL FORMULARIO INTEGRADO */
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<h1 style='text-align:center; color:white; font-size: 55px; font-weight: 900; margin-bottom: 0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366; font-size: 20px; font-weight: bold; margin-top: -10px;'>CENTRAL LOGÍSTICA SAN JORGE</p>", unsafe_allow_html=True)
st.write("---")

# 4. FORMULARIO INTEGRADO (Dentro de un expander con estilo)
with st.expander("📝 PUBLICAR MI CAMIÓN (Completar aquí)"):
    with st.form("form_nuevo_viaje", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ori = st.text_input("📍 Desde dónde salís (Origen)", placeholder="Ej: San Jorge")
            equ = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico", "Batea"])
        with c2:
            des = st.text_input("🏁 A dónde vas (Destino)", placeholder="Ej: Rosario")
            tel = st.text_input("📱 WhatsApp (Ej: 3406123456)", placeholder="Sin el + ni espacios")
        
        btn_enviar = st.form_submit_button("🚀 PUBLICAR AHORA", use_container_width=True)
        
        if btn_enviar:
            if ori and des and tel:
                # Aquí enviamos a tu Google Form real
                FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/formResponse"
                # Estos entry IDs son ejemplos, recordá que si los tenés correctos se carga al Excel
                payload = {
                    "entry.1834914102": ori, 
                    "entry.1121303831": des, 
                    "entry.1018903264": equ, 
                    "entry.1437637841": tel
                }
                try:
                    requests.post(FORM_URL, data=payload)
                    st.success("✅ ¡Publicado! Dale al botón 'ACTUALIZAR' debajo para verlo en la lista.")
                except:
                    st.error("Hubo un problema. Intentá de nuevo.")
            else:
                st.warning("Completá todos los datos para publicar.")

# 5. LISTADO DE VIAJES (Conexión directa)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"

try:
    df = pd.read_csv(URL)
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    df = df.dropna(subset=['origen'])

    # CONTROLES
    col_busq, col_refr = st.columns([3, 1])
    with col_busq:
        search = st.text_input("", placeholder="🔍 Buscar ciudad, destino o equipo...")
    with col_refr:
        if st.button("🔄 ACTUALIZAR LISTA", use_container_width=True):
            st.rerun()

    # TARJETAS
    if not df.empty:
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False) |
                    df['equipo'].str.contains(search, case=False, na=False)]

        for _, row in df.iloc[::-1].iterrows():
            tel_limpio = "".join(filter(str.isdigit, str(row['tel'])))
            mensaje = urllib.parse.quote(f"Hola! Vi tu camión de {row['origen']} a {row['destino']} en Retorno Match. ¿Seguís disponible?")
            link_wa = f"https://wa.me/{tel_limpio}?text={mensaje}"
            
            st.markdown(f"""
            <div class="camion-card">
                <div>
                    <p class="route-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                    <p class="detail-text">🚛 <b>EQUIPO:</b> {row['equipo']}</p>
                    <p class="fecha-text">📅 Publicado: {row['fecha']}</p>
                </div>
                <a href="{link_wa}" target="_blank" class="btn-wa">📱 CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay camiones reportados aún.")

except Exception as e:
    st.warning("Sincronizando con el listado de San Jorge...")

st.markdown("<br><p style='text-align:center; color:white; opacity:0.5;'>San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
