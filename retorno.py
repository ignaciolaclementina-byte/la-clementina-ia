import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# 2. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card-viaje { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; color: black; border-left: 10px solid #2ecc71; }
    .btn-ws { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9lMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    # LEER LA HOJA "cargas" (Asegurate que se llame así en el Excel)
    try:
        df = conn.read(spreadsheet=URL_DB, worksheet="cargas") # <--- CAMBIO CLAVE AQUÍ
        if not df.empty:
            df.columns = df.columns.str.strip().str.lower()
            for _, r in df.iloc[::-1].iterrows():
                if pd.notna(r.get('origen')):
                    tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
                    st.markdown(f"""
                    <div class="card-viaje">
                        <h3>📍 {str(r['origen']).upper()}</h3>
                        <p>📦 <b>Carga:</b> {r.get('item', 'N/A')} | 💰 <b>Tarifa:</b> {r.get('pago', 'A convenir')}</p>
                        <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR</a>
                    </div>
                    """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error al leer la hoja 'cargas': {e}")

with tab2:
    st.markdown("<h3 style='color: white;'>Publicar nuevo viaje</h3>", unsafe_allow_html=True)
    with st.form("form_nuevo", clear_on_submit=True):
        origen = st.text_input("¿Desde dónde salís?")
        item = st.text_input("¿Qué llevás o buscás?")
        pago = st.text_input("Tarifa / Pago")
        tel = st.text_input("WhatsApp (Ej: 3406400000)")
        
        if st.form_submit_button("PUBLICAR AHORA"):
            if origen and tel:
                # 1. Traer datos actuales de la hoja "cargas"
                current_df = conn.read(spreadsheet=URL_DB, worksheet="cargas")
                # 2. Crear nueva fila
                nuevo = pd.DataFrame([{"origen": origen, "item": item, "pago": pago, "tel": tel}])
                # 3. Unir y subir
                updated_df = pd.concat([current_df, nuevo], ignore_index=True)
                conn.update(spreadsheet=URL_DB, data=updated_df, worksheet="cargas")
                
                st.success("¡Publicado! Revisá la pestaña 'BUSCAR VIAJES'.")
                st.balloons()
            else:
                st.warning("Completá origen y teléfono.")
