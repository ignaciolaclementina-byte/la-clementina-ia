import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. ESTILO
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .camion-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
        overflow: hidden;
    }
    .card-header { background: #f8f9fa; padding: 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
    .btn-wa { background: #25D366; color: white !important; text-align: center; padding: 12px; display: block; text-decoration: none; font-weight: bold; border-radius: 0 0 15px 15px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. BOTONES
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.rerun()
with col3:
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScWcPChu8-wqWSijj9IoA5ES6CunJOJTirhPvqXKHkl_sy9MA/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

st.write("---")

# 4. DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(URL)
    
    # Forzamos los nombres de columnas para que coincidan con el formulario
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    
    search = st.text_input("", placeholder="🔍 Buscar destino...")

    if search:
        df = df[df['destino'].str.contains(search, case=False, na=False) | 
                df['origen'].str.contains(search, case=False, na=False)]

    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                tel = str(row['tel']).split('.')[0].replace(" ", "").replace("+", "")
                msg = urllib.parse.quote(f"Hola! Vi tu camion de {row['origen']} a {row['destino']} en Retorno Match.")
                
                st.markdown(f"""
                <div class="camion-card">
                    <div class="card-header">
                        <span style="font-weight:bold; font-size:18px; color:black;">📍 {row['origen']} ⮕ {row['destino']}</span>
                        <span style="color:green; font-weight:bold;">● DISPONIBLE</span>
                    </div>
                    <div style="padding:15px; color:#333;">
                        <p style="margin:0;"><b>Equipo:</b> {row['equipo']}</p>
                        <p style="margin:0; font-size:12px; color:grey;">Publicado: {row['fecha']}</p>
                    </div>
                    <a href="https://wa.me/{tel}?text={msg}" target="_blank" class="btn-wa">WHATSAPP</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No hay camiones publicados todavía.")

except Exception as e:
    st.info("Esperando datos del formulario...")

st.markdown("<br><p style='text-align:center; color:white; font-size:10px;'>San Jorge 2026</p>", unsafe_allow_html=True)
