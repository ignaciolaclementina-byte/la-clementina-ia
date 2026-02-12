import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y ESTILO PRO
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; border-left: 10px solid #2ecc71; box-shadow: 0 4px 8px rgba(0,0,0,0.3); }
    .card h3 { color: #1a1a1a; margin: 0; font-size: 1.4rem; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. LOS LINKS DEFINITIVOS
# Tu link de lectura CSV
URL_LECTURA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# Tu link de Formulario (ya con el truco para que encaje)
LINK_FORMULARIO = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

# 3. INTERFAZ PRINCIPAL
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJE / CAMIÓN", "📤 PUBLICAR AHORA"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 ACTUALIZAR LISTA"):
            st.cache_data.clear()
            st.rerun()
    
    try:
        # Leemos el Excel
        df = pd.read_csv(URL_LECTURA)
        
        # Filtramos filas vacías basándonos en la columna de Ciudad (Columna 1)
        df = df.dropna(subset=[df.columns[1]]) 
        
        # Invertimos el orden (lo último cargado arriba)
        for _, r in df.iloc[::-1].iterrows(): 
            # r.iloc[0] es la hora, r.iloc[1] es Ciudad, etc.
            ciudad = str(r.iloc[1]).upper()
            detalle = str(r.iloc[2])
            pago = str(r.iloc[3])
            tel = str(r.iloc[4]).split('.')[0].replace(" ", "").replace("+", "")
            
            st.markdown(f"""
            <div class="card">
                <h3>📍 {ciudad}</h3>
                <p>📦 <b>Detalle:</b> {detalle}</p>
                <p>💰 <b>Pago/Tarifa:</b> {pago}</p>
                <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR POR WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("Buscando nuevas cargas en el sistema...")

with tab2:
    # Mostramos el formulario nativo de Google dentro de la App
    components.iframe(LINK_FORMULARIO, height=800, scrolling=True)
