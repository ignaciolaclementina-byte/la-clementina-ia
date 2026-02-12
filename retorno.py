import streamlit as st
import pandas as pd

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="centered")

# Estilo personalizado para que se vea bien en el celu
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007bff; color: white; }
    .viaje-card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #007bff; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# ID de tu planilla (sacado de tu link)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

if st.button("🔄 ACTUALIZAR VIAJES"):
    st.rerun()

try:
    # Leemos la solapa "cargas" directamente
    df = pd.read_csv(URL)
    
    # Limpiar nombres de columnas por las dudas
    df.columns = [c.strip().lower() for c in df.columns]
    
    st.subheader("📍 Viajes Disponibles")
    
    if not df.empty:
        # Mostramos los viajes del más nuevo al más viejo
        for _, row in df.iloc[::-1].iterrows():
            with st.container():
                st.markdown(f"""
                <div class="viaje-card">
                    <h3 style='margin:0;'>{str(row['origen']).upper()} ➡️ {str(row['item']).capitalize()}</h3>
                    <p style='margin:5px 0;'>💰 <b>Pago:</b> {row['pago']}</p>
                    <p style='margin:0;'>📞 <b>Contacto:</b> {row['tel']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay viajes cargados en la planilla todavía.")

except Exception as e:
    st.error("⚠️ Error al conectar. Asegurate de que el Google Sheets esté compartido como 'Cualquier persona con el enlace'.")
    st.info("Hacé clic en 'Compartir' -> 'Acceso general' -> 'Cualquier persona con el enlace' en tu Excel.")

st.markdown("---")
st.caption("Para publicar un viaje, cargalo en el Google Sheets.")
