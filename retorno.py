import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# Estilo visual pro
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid #2ecc71; color: black; }
    .card h3 { margin-top:0; color: #1a1a1a; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN DIRECTA (Sin demoras de "Publicar en la web")
# Usamos el link de edición, pero la App lo usará como base de datos
url = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INTERFAZ
st.title("🚛 RETORNO MATCH - SAN JORGE")

tab1, tab2 = st.tabs(["🔍 BUSCAR DISPONIBLES", "📤 PUBLICAR (CARGA O CAMIÓN)"])

with tab1:
    # Leemos los datos actuales
    data = conn.read(spreadsheet=url, usecols=[0,1,2,3])
    data = data.dropna(subset=[data.columns[0]]) # Limpiar filas vacías
    
    for _, row in data.iterrows():
        st.markdown(f"""
            <div class="card">
                <h3>📍 {row.iloc[0]}</h3>
                <p><b>Detalle:</b> {row.iloc[1]}</p>
                <p><b>Pago/Tipo:</b> {row.iloc[2]}</p>
                <p><b>Teléfono:</b> {row.iloc[3]}</p>
                <a href="https://wa.me/549{row.iloc[3]}" target="_blank" style="color: green; font-weight: bold;">📲 Contactar por WhatsApp</a>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("Completá los datos para publicar")
    with st.form(key="publicar_form"):
        tipo = st.selectbox("¿Qué publicás?", ["Carga Disponible", "Camión Buscando Retorno"])
        origen = st.text_input("Origen / Ubicación actual")
        detalle = st.text_input("¿Qué llevás? / ¿Qué buscás? (Ej: Maíz / Térmico)")
        pago = st.text_input("Pago ofrecido / Tarifa")
        tel = st.text_input("Tu WhatsApp (Ej: 3406649346)")
        
        submit_button = st.form_submit_button(label="🚀 PUBLICAR AHORA")
        
        if submit_button:
            # Aquí creamos la nueva fila
            new_data = pd.DataFrame([{"origen": origen, "item": detalle, "pago": pago, "tel": tel}])
            # Actualizamos el Excel
            updated_df = pd.concat([data, new_data], ignore_index=True)
            conn.update(spreadsheet=url, data=updated_df)
            st.success("¡Publicado con éxito! Refrescá la pestaña de búsqueda.")
            st.balloons()
