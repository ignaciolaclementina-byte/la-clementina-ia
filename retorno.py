import streamlit as st
import pandas as pd

# Configuración de página para forzar el modo claro original
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- DISEÑO PROFESIONAL CON FONDO ORIGINAL ---
st.markdown("""
    <style>
    /* Forzamos el fondo claro original de Streamlit */
    .stApp {
        background-color: #f8f9fb;
    }
    
    /* Título principal en negro para que resalte */
    h1 {
        color: #1E1E1E !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        text-align: center;
    }

    /* Tarjetas de viajes: fondo blanco puro sobre el gris claro */
    .viaje-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        border-left: 10px solid #28a745; /* Verde camión profesional */
        margin-bottom: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    
    .viaje-card h2 {
        color: #1E1E1E !important;
        margin: 0;
        font-size: 24px;
        border: none;
    }
    
    .viaje-card p {
        margin: 10px 0 0 0;
        color: #333333 !important;
        font-size: 18px;
        line-height: 1.5;
    }

    /* Botón de actualizar en azul profesional */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# Conexión directa al Excel (Link público)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR LISTADO DE VIAJES"):
    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

try:
    # Carga de datos
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    if not df.empty:
        st.subheader("📍 Viajes Disponibles")
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Estructura de la tarjeta
                st.markdown(f"""
                <div class="viaje-card">
                    <h2>📍 {str(row['origen']).upper()} ➡️ {str(row['item']).upper()}</h2>
                    <p>💵 <b>PAGO:</b> {row['pago']}</p>
                    <p>📞 <b>CONTACTO:</b> {row['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes cargados en la planilla.")

except Exception as e:
    st.error("Error al conectar con el listado. Revisá la planilla de Excel.")

st.markdown("---")
st.caption("Los datos se actualizan desde Google Sheets.")
