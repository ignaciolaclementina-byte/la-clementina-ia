import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- DISEÑO PROFESIONAL CON IMAGEN DE FONDO ---
st.markdown("""
    <style>
    /* 1. Ponemos la imagen de fondo (un camión profesional) */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* 2. Título con sombra para que resalte */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 4px #000000;
        font-weight: 800;
        text-align: center;
        padding-bottom: 20px;
    }

    /* 3. Tarjetas de viajes con efecto "vidrio" (Glassmorphism) */
    .viaje-card {
        background-color: rgba(255, 255, 255, 0.95); /* Blanco casi sólido para legibilidad total */
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #28a745;
        margin-bottom: 20px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.3);
    }
    
    .viaje-card h2 {
        color: #1a1a1a !important;
        margin: 0;
        font-size: 22px;
        font-weight: bold;
    }
    
    .viaje-card p {
        margin: 10px 0 0 0;
        color: #333333 !important;
        font-size: 19px;
    }

    /* 4. Botón Moderno */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        height: 3.5em;
        background-color: #28a745;
        color: white;
        font-weight: bold;
        border: 2px solid white;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }
    
    /* Subtítulos en blanco */
    .stMarkdown h3 {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# ID de tu planilla
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR LISTADO DE VIAJES"):
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
                    <p>💵 <b>PAGO:</b> <span style='color:#28a745; font-weight:bold;'>{row['pago']}</span></p>
                    <p>📞 <b>TEL:</b> <span style='font-family:monospace; font-weight:bold;'>{row['tel']}</span></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes publicados.")

except Exception as e:
    st.error("Error al cargar datos.")

st.markdown("---")
st.caption("Sincronizado con Google Sheets")
