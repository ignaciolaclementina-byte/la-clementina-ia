import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA Y FONDO
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
             background-attachment: fixed;
             background-size: cover;
         }}
         .viaje-card {{
             background: white; 
             padding: 25px; 
             border-radius: 15px; 
             border-left: 12px solid #2ecc71;
             margin-bottom: 25px;
             box-shadow: 0 10px 20px rgba(0,0,0,0.5);
         }}
         .viaje-card h3, .viaje-card p {{ color: #1a1a1a !important; margin: 10px 0; }}
         .btn-ws {{
             background-color: #25D366;
             color: white !important;
             text-align: center;
             padding: 15px;
             border-radius: 10px;
             text-decoration: none;
             display: block;
             font-weight: bold;
             font-size: 18px;
             margin-top: 15px;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

# 2. LINK DE PUBLICACIÓN (EL QUE FUNCIONA)
URL_FINAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# 3. MENÚ SUPERIOR (TABS)
tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR", "📩 PUBLICAR", "🚛 CAMIONES"])

with tab1:
    st.markdown("<h1 style='text-align: center; color: white;'>🚚 RETORNO MATCH</h1>", unsafe_allow_html=True)
    
    try:
        df = pd.read_csv(URL_FINAL)
        df.columns = df.columns.str.strip().str.lower()
        
        if not df.empty:
            viajes = df.dropna(subset=['origen'])
            
            # Buscador por ciudad
            busqueda = st.text_input("Filtrar por ciudad de origen:", "").lower()
            
            for _, r in viajes.iterrows():
                origen = str(r['origen'])
                if busqueda in origen.lower():
                    tel_limpio = str(r.get('tel', '')).split('.')[0].replace(" ", "").replace("+", "")
                    
                    st.markdown(f"""
                    <div class='viaje-card'>
                        <h3>📍 {origen.upper()}</h3>
                        <p>📦 <b>Carga:</b> {r.get('item', '-')}</p>
                        <p>💰 <b>Pago:</b> ${r.get('pago', '-')}</p>
                        <p>📲 <b>WhatsApp:</b> {r.get('tel', '-')}</p>
                        <a class='btn-ws' href='https://wa.me/549{tel_limpio}' target='_blank'>ENVIAR WHATSAPP</a>
                    </div>
                    """, unsafe_allow_html=True)
        
        if st.button("🔄 ACTUALIZAR DATOS"):
            st.rerun()

    except Exception as e:
        st.error("Error cargando datos. Verificá que el Excel esté publicado.")

with tab2:
    st.markdown("<h2 style='color: white;'>Publicá tu carga</h2>", unsafe_allow_html=True)
    st.info("Para publicar, cargá los datos en tu planilla de Excel y aparecerán automáticamente aquí.")
    st.markdown(f"[🔗 Abrir mi planilla de Excel](https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS/edit)")

with tab3:
    st.markdown("<h2 style='color: white;'>Camiones Disponibles</h2>", unsafe_allow_html=True)
    st.write("Próximamente verás aquí la lista de camiones buscando retorno.")
