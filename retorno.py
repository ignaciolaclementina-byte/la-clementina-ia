import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    /* Estilo general del título */
    h1 {
        color: #1E1E1E;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
    }
    
    /* Tarjetas de viajes limpias (estilo original) */
    .viaje-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E0E0E0;
        border-left: 6px solid #2E7D32; /* Verde transporte profesional */
        margin-bottom: 15px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    
    .viaje-card h3 {
        color: #1E1E1E;
        margin: 0;
        font-size: 20px;
        display: flex;
        align-items: center;
    }
    
    .viaje-card p {
        margin: 8px 0 0 0;
        color: #444444;
        font-size: 16px;
    }

    /* Botón de actualizar */
    .stButton>button {
        background-color: #1E1E1E;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2E7D32;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# ID de tu planilla
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR LISTADO"):
    st.rerun()

st.markdown("---")

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Diseño de tarjeta profesional
                st.markdown(f"""
                <div class="viaje-card">
                    <h3>📍 {str(row['origen']).upper()} ➡️ {str(row['item']).upper()}</h3>
                    <p>💵 <b>PAGO:</b> {row['pago']}</p>
                    <p>📞 <b>CONTACTO:</b> {row['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes publicados por el momento.")

except Exception as e:
    st.error("Error al conectar con la base de datos.")

st.markdown("---")
st.caption("Los datos se sincronizan automáticamente con el Google Sheets.")
