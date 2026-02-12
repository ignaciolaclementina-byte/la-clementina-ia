import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# CONFIGURACIÓN VISUAL
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; border-left: 10px solid #2ecc71; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# LINKS DEFINITIVOS
URL_LECTURA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"
LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSd8BBZZ563XiGaEoYCg_bfmDN3hLsG7jcING2B2PGAEJDPbhQ/viewform?embedded=true"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR DISPONIBLES", "📤 PUBLICAR AHORA"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTA"):
        st.cache_data.clear()
        st.rerun()
    
    try:
        # Leemos el Excel que genera el Formulario
        df = pd.read_csv(URL_LECTURA)
        
        # Saltamos la primera fila si tiene encabezados y filtramos vacíos
        df = df.dropna(subset=[df.columns[1]]) 
        
        # Mostramos de más nuevo a más viejo
        for _, r in df.iloc[::-1].iterrows():
            # Asumiendo: r.iloc[1]=Ciudad, r.iloc[2]=Detalle, r.iloc[3]=Pago, r.iloc[4]=WhatsApp
            st.markdown(f"""
            <div class="card">
                <h3>📍 {str(r.iloc[1]).upper()}</h3>
                <p>📦 <b>Detalle:</b> {r.iloc[2]}</p>
                <p>💰 <b>Pago/Tarifa:</b> {r.iloc[3]}</p>
                <a class="btn-ws" href="https://wa.me/549{str(r.iloc[4]).split('.')[0]}" target="_blank">📲 CONTACTAR</a>
            </div>
            """, unsafe_allow_html=True)
    except:
        st.info("No hay publicaciones recientes. ¡Sé el primero en publicar!")

with tab2:
    # El formulario incrustado
    components.iframe(LINK_FORM, height=700, scrolling=True)
