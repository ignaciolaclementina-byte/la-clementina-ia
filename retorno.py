import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- ESTILO PARA FONDO OSCURO CON TARJETAS LEGIBLES ---
st.markdown("""
    <style>
    /* Fondo general oscuro */
    .main { background-color: #0e1117; }
    
    /* Tarjetas semi-transparentes para que se vea el fondo */
    .viaje-card {
        background-color: rgba(255, 255, 255, 0.05); /* Fondo muy suave */
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 8px solid #007bff;
        margin-bottom: 15px;
        backdrop-filter: blur(10px); /* Efecto de desenfoque */
    }
    
    /* Colores de texto para fondo oscuro */
    .viaje-card h3 { color: #007bff; margin-top: 0; margin-bottom: 10px; font-size: 22px; }
    .viaje-card p { margin: 5px 0; font-size: 18px; color: #e0e0e0; }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR LISTADO"):
    st.rerun()

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    st.markdown("### 📍 Viajes Disponibles")
    
    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                st.markdown(f"""
                <div class="viaje-card">
                    <h3>{str(row['origen']).upper()} ➡️ {str(row['item']).capitalize()}</h3>
                    <p>💰 <b>Pago:</b> <span style='color:#4cd137;'>{row['pago']}</span></p>
                    <p>📞 <b>Contacto:</b> <span style='color:#fbc531;'>{row['tel']}</span></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes publicados por el momento.")

except Exception as e:
    st.error("Error al cargar los datos.")

st.markdown("---")
st.caption("Cargá los viajes en tu Google Sheets para que aparezcan acá.")
