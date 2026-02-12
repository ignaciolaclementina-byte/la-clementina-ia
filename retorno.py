import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# --- ESTILO CORREGIDO PARA QUE SE VEA BIEN ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .viaje-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 8px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        color: #1f1f1f; /* Color de texto oscuro para que se lea */
    }
    .viaje-card h3 { color: #007bff; margin-top: 0; margin-bottom: 10px; font-size: 22px; }
    .viaje-card p { margin: 5px 0; font-size: 18px; color: #333333; }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# Tu ID de planilla
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR LISTADO"):
    st.rerun()

try:
    # Leemos la planilla
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    st.markdown("### 📍 Viajes Disponibles")
    
    if not df.empty:
        # Mostramos los viajes con el nuevo diseño
        for _, row in df.iloc[::-1].iterrows():
            # Validamos que no sea una fila vacía
            if pd.notna(row['origen']):
                st.markdown(f"""
                <div class="viaje-card">
                    <h3>{str(row['origen']).upper()} ➡️ {str(row['item']).capitalize()}</h3>
                    <p>💰 <b>Pago:</b> {row['pago']}</p>
                    <p>📞 <b>Contacto:</b> {row['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes publicados por el momento.")

except Exception as e:
    st.error("Error al cargar los datos. Revisá que el Excel tenga las columnas: origen, item, pago, tel")

st.markdown("---")
st.caption("Cargá los viajes en tu Google Sheets para que aparezcan acá.")
