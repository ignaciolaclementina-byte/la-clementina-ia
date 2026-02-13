import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    .camion-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. BOTÓN DE PUBLICAR
col1, col2, col3 = st.columns([1,1,1])
with col2:
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

st.write("---")

# 4. CARGA DE DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Conectamos a la hoja que vimos en tu Excel
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%202"

try:
    df = pd.read_csv(URL)
    
    # Limpiamos columnas vacías y nos quedamos con las que tienen datos según tu captura
    # Mapeamos: Marca Temporal (A), Ubicación (G), Destino (H), Equipo (I), WhatsApp (E o F)
    # Para no fallar, buscamos los nombres exactos que puso Google:
    
    columnas_necesarias = {
        'Marca temporal': 'fecha',
        'Ubicación Actual': 'origen',
        'Destino del Retorno': 'destino',
        'Tipo de Equipo': 'equipo',
        'whatsapp': 'tel'
    }
    
    # Renombramos solo las que existen
    df = df.rename(columns=columnas_necesarias)
    
    # Buscador
    search = st.text_input("", placeholder="🔍 Buscar por ciudad (Ej: Rosario, Córdoba...)")

    if not df.empty:
        # Mostramos solo filas que tengan Origen (para evitar las vacías del medio)
        df_validos = df[df['origen'].notna()]
        
        if search:
            df_validos = df_validos[df_validos['destino'].str.contains(search, case=False, na=False) | 
                                   df_validos['origen'].str.contains(search, case=False, na=False)]

        for _, row in df_validos.iloc[::-1].iterrows():
            # Limpiar teléfono
            tel_sucio = str(row['tel']).split('.')[0]
            tel_final = "".join(filter(str.isdigit, tel_sucio))
            
            # Mensaje de WhatsApp (sin f-string compleja para evitar el error anterior)
            texto = "Hola! Vi tu camion de " + str(row['origen']) + " a " + str(row['destino']) + " en Retorno Match."
            msg = urllib.parse.quote(texto)
            
            st.markdown(f"""
            <div class="camion-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h3 style="color: black; margin:0;">📍 {str(row['origen']).upper()} ⮕ {str(row['destino']).upper()}</h3>
                        <p style="color: #444; margin: 5px 0;"><b>🚛 Equipo:</b> {row['equipo']}</p>
                        <small style="color: #888;">Publicado: {row['fecha']}</small>
                    </div>
                    <a href="https://wa.me/{tel_final}?text={msg}" target="_blank" class="btn-wa">📱 WHATSAPP</a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Esperando nuevos registros...")

except Exception as e:
    st.info("Sincronizando con el listado de camiones...")

st.markdown("<br><p style='text-align:center; color:white; opacity:0.6; font-size:12px;'>San Jorge 2026</p>", unsafe_allow_html=True)
