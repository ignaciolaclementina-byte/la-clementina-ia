import streamlit as st
import pandas as pd

# 1. CONFIGURACION
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. CONEXION (Link directo a CSV para evitar errores)
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=669889309"

# 3. DISEÑO
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    h1, h2, h3, p, label, .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .info-box { background: white; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 8px solid #2ecc71; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
    .info-box p, .info-box h3 { color: #2c3e50 !important; margin: 2px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. FUNCION CARGAR CON REINTENTO
def cargar_datos(url):
    try:
        # Forzamos la lectura sin usar caché del navegador
        df = pd.read_csv(url, on_bad_lines='skip')
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return pd.DataFrame()

df_ca = cargar_datos(URL_CARGAS)
df_cam = cargar_datos(URL_CAMIONES)

# 5. PESTAÑAS
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 CAMIONES"])

with t1:
    if not df_ca.empty and 'origen' in df_ca.columns:
        # Buscamos solo filas que tengan un origen escrito
        datos = df_ca.dropna(subset=['origen'])
        if not datos.empty:
            for _, r in datos.iterrows():
                st.markdown(f"""
                <div class='info-box'>
                    <h3>📍 {r['origen'].upper()}</h3>
                    <p>📦 <b>Carga:</b> {r.get('item', 'Varios')}</p>
                    <p>💰 <b>Pago:</b> ${r.get('pago', 'A convenir')}</p>
                    <p>📲 <b>WhatsApp:</b> {r.get('tel', 'Sin número')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("El Excel está conectado pero parece estar vacío.")
    else:
        st.error("Error de conexión. Revisá que el Excel esté en 'Cualquier persona con el enlace'.")

with t2:
    st.info("Aquí pondremos los formularios de Google pronto.")

with t3:
    if not df_cam.empty:
        st.write("Camiones disponibles aparecerán aquí.")
    else:
        st.write("No hay camiones reportados.")
