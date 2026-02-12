import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- ESTILO DEFINITIVO (FONDO + TARJETAS PROFESIONALES) ---
st.markdown("""
    <style>
    /* Imagen de fondo fija */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Título principal */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 8px #000000;
        font-weight: 800;
        text-align: center;
    }

    /* Tarjetas blancas de alta visibilidad */
    .viaje-card {
        background-color: rgba(255, 255, 255, 0.98); 
        padding: 25px;
        border-radius: 15px;
        border-left: 12px solid #28a745;
        margin-bottom: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.5);
    }
    
    .viaje-card h2 {
        color: #1a1a1a !important;
        margin: 0;
        font-size: 24px;
        font-weight: bold;
        border: none;
    }
    
    .viaje-card p {
        margin: 12px 0 0 0;
        color: #333333 !important;
        font-size: 20px;
        font-weight: 500;
    }

    /* Botón verde redondeado */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        background-color: #28a745;
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: 2px solid white;
    }
    
    /* Texto de sección */
    .stMarkdown h3 {
        color: white !important;
        text-shadow: 1px 1px 3px black;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# Conexión al Sheets
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("✅ ACTUALIZAR LISTADO DE VIAJES"):
    st.rerun()

st.markdown("### 📍 Viajes Disponibles")

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                st.markdown(f"""
                <div class="viaje-card">
                    <h2>📍 {str(row['origen']).upper()} ➡️ {str(row['item']).upper()}</h2>
                    <p>💵 <b>PAGO:</b> <span style='color:#28a745;'>{row['pago']}</span></p>
                    <p>📞 <b>TEL:</b> {row['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes cargados.")
except Exception as e:
    st.error("Error de conexión.")

st.markdown("<br><p style='text-align:center; color:white;'>Sincronizado con Google Sheets</p>", unsafe_allow_html=True)
