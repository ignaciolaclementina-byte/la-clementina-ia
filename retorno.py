import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# ESTILO VISUAL (FONDO Y TARJETAS)
st.markdown("""
    <style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; background-attachment: fixed; }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; border-left: 10px solid #2ecc71; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- TU LINK DE "PUBLICAR EN LA WEB" ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"

# LINK DE TU FORMULARIO
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR CARGAS", "📤 PUBLICAR AHORA"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Leemos el Excel desde el link de publicación
        df = pd.read_csv(URL_CSV)
        
        # Limpiamos nombres de columnas por si acaso
        df.columns = df.columns.str.strip().str.lower()
        
        # Filtramos filas donde 'origen' esté vacío
        df = df.dropna(subset=['origen']) 
        
        # Mostramos de más nuevo a más viejo
        for _, r in df.iloc[::-1].iterrows():
            # Limpiamos el teléfono para el link de WhatsApp
            tel_limpio = str(r['tel']).split('.')[0].replace(" ", "").replace("+", "")
            
            st.markdown(f"""
            <div class="card">
                <h3 style="margin:0;">📍 {str(r['origen']).upper()}</h3>
                <p style="margin:5px 0;">📦 <b>Carga:</b> {r['item']}</p>
                <p style="margin:5px 0;">💰 <b>Tarifa:</b> {r['pago']}</p>
                <a class="btn-ws" href="https://wa.me/549{tel_limpio}" target="_blank">📲 CONTACTAR WHATSAPP</a>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.info("No hay cargas publicadas en este momento.")

with tab2:
    # Mostramos el formulario para que la gente cargue datos
    st.markdown("<div style='background: white; border-radius: 15px; padding: 10px;'>", unsafe_allow_html=True)
    components.iframe(URL_FORM, height=800, scrolling=True)
    st.markdown("</div>", unsafe_allow_html=True)
