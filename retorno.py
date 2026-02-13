import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. ESTILO VISUAL PREMIUM
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
    }
    .camion-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 8px solid #00FF41;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .btn-wa {
        background: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. CONEXIÓN A LA BASE DE DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Esta URL intenta buscar la última pestaña de respuestas creada
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

try:
    df = pd.read_csv(URL)
    
    # Limpieza: Eliminamos columnas totalmente vacías que a veces crea Google
    df = df.dropna(axis=1, how='all')
    
    # Renombramos a nombres simples para el código
    # Esperamos: [Fecha, Origen, Destino, Equipo, WhatsApp]
    if len(df.columns) >= 5:
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'whatsapp'] + list(df.columns[5:])

    # 4. BUSCADOR
    search = st.text_input("", placeholder="🔍 ¿A dónde buscás retorno? (Ej: Rosario, Córdoba...)")

    # 5. MOSTRAR CARGAS
    if not df.empty:
        # Filtrar si hay búsqueda
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                tel = str(row['whatsapp']).split('.')[0].replace(" ", "").replace("+", "")
                msg = urllib.parse.quote(f"Hola! Vi tu retorno de {row['origen']} a {row['destino']} en Retorno Match.")
                
                st.markdown(f"""
                <div class="camion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="color: black; margin:0;">📍 {str(row['origen']).upper()} ⮕ {str(row['destino']).upper()}</h3>
                            <p style="color: #666; margin: 5px 0;"><b>🚛 Equipo:</b> {row['equipo']}</p>
                            <small style="color: #999;">Publicado: {row['fecha']}</small>
                        </div>
                        <a href="https://wa.me/{tel}?text={msg}" target="_blank" class="btn-wa">📱 CONTACTAR</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay camiones disponibles por el momento.")

except Exception as e:
    st.warning("Configurando conexión con el formulario...")

# Botón para publicar al final
st.write("---")
LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScWcPChu8-wqWSijj9IoA5ES6CunJOJTirhPvqXKHkl_sy9MA/viewform"
st.link_button("➕ PUBLICAR MI CAMIÓN AQUÍ", LINK_FORM, use_container_width=True)
