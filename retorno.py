import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# ESTILO VISUAL (Fondo y tarjetas)
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

# CONEXIÓN A GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)
URL_DB = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9lMC06jZG0uLiOs/edit#gid=0"

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR VIAJES", "📤 PUBLICAR MI RETORNO"])

with tab1:
    if st.button("🔄 ACTUALIZAR LISTADO"):
        st.cache_data.clear()
        st.rerun()
    
    # Leer datos reales
    df = conn.read(spreadsheet=URL_DB, worksheet="0")
    if not df.empty:
        df.columns = df.columns.str.strip().str.lower()
        # Mostrar de más nuevo a más viejo
        for _, r in df.iloc[::-1].iterrows():
            if pd.notna(r['origen']):
                tel = str(r['tel']).split('.')[0]
                st.markdown(f"""
                <div class="card-viaje">
                    <h3>📍 {str(r['origen']).upper()}</h3>
                    <p>📦 <b>Carga:</b> {r['item']} | 💰 <b>Tarifa:</b> {r['pago']}</p>
                    <a class="btn-ws" href="https://wa.me/549{tel}" target="_blank">📲 CONTACTAR</a>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("<h3 style='color: white;'>Publicar nuevo viaje</h3>", unsafe_allow_html=True)
    with st.form("nuevo_viaje", clear_on_submit=True):
        origen = st.text_input("¿Desde dónde salís?")
        item = st.text_input("¿Qué llevás o buscás?")
        pago = st.text_input("Tarifa / Pago")
        tel = st.text_input("WhatsApp (Ej: 3406400000)")
        
        if st.form_submit_button("PUBLICAR AHORA"):
            if origen and tel:
                # 1. Traer datos actuales
                current_df = conn.read(spreadsheet=URL_DB, worksheet="0")
                # 2. Crear nueva fila
                nuevo = pd.DataFrame([{"origen": origen, "item": item, "pago": pago, "tel": tel}])
                # 3. Combinar y subir
                updated_df = pd.concat([current_df, nuevo], ignore_index=True)
                conn.update(spreadsheet=URL_DB, data=updated_df)
                
                st.success("¡Publicado en el Excel!")
                st.balloons()
            else:
                st.error("Faltan datos obligatorios.")
