import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO VISUAL (Para que parezca una App profesional)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    .camion-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        font-size: 18px;
    }
    .route-title {
        color: #1a1a1a;
        font-size: 24px;
        font-weight: 900;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white; font-size: 60px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00FF41; font-weight:bold;'>CENTRAL DE LOGÍSTICA SAN JORGE</p>", unsafe_allow_html=True)

# 3. BOTONES DE ACCIÓN
col1, col2, col3 = st.columns([1,1,1])
with col2:
    # Este es el link limpio de tu nuevo formulario
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True, type="primary")

st.write("---")

# 4. CARGA DE DATOS DESDE EL EXCEL
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# IMPORTANTE: Asegurate que la pestaña nueva se llame 'Respuestas de formulario 1'
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(URL)
    
    # Forzamos los nombres de columnas para que el código no se pierda
    # [Marca temporal, origen, destino, equipo, whatsapp]
    df = df.iloc[:, :5] 
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'whatsapp']

    # BUSCADOR
    search = st.text_input("", placeholder="🔍 ¿A qué ciudad buscás carga? (Ej: Rosario, Buenos Aires...)")

    if not df.empty:
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        # Mostrar de la más nueva a la más vieja
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Limpiamos el WhatsApp (por si tiene espacios o .0)
                tel = str(row['whatsapp']).split('.')[0].replace(" ", "").replace("+", "")
                msg = urllib.parse.quote(f"Hola! Vi en Retorno Match que tenés un
