import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO VISUAL (El diseño "Lindo" original)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    .camion-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366; /* Borde verde característico */
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .card-content h3 {
        color: #1a1a1a;
        margin: 0 0 5px 0;
        font-size: 24px;
        font-weight: 800;
    }
    .card-content p {
        color: #555;
        margin: 0;
        font-size: 16px;
    }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(37, 211, 102, 0.4);
    }
    .btn-wa:hover {
        background-color: #1ebc57;
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

# TÍTULO PRINCIPAL
st.markdown("<h1 style='text-align:center; color:white; font-size: 55px; font-weight: 900; margin-bottom: 0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#00FF41; font-size: 18px; margin-top: -10px;'>LOGÍSTICA SAN JORGE - CONECTANDO CARGAS</p>", unsafe_allow_html=True)
st.write("---")

# 3. CONEXIÓN A LA BASE DE DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
# IMPORTANTE: Aquí apuntamos a la pestaña 3 que se ve en tu foto
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203"

try:
    df = pd.read_csv(URL)
    
    # En tu foto 'image_beb3fb.png' las columnas están perfectas:
    # A: Marca temporal | B: origen | C: destino | D: equipo | E: whatsapp
    # Tomamos solo las primeras 5 columnas
    df = df.iloc[:, :5]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    
    # FILTRO: Eliminamos filas vacías (si alguien borró datos)
    df = df.dropna(subset=['origen', 'destino'])

    # 4. INTERFAZ DE BÚSQUEDA
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        search = st.text_input("", placeholder="🔍 Buscar ciudad (Ej: Rosario, Córdoba...)")
    with col_btn:
        LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSc-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform"
        st.link_button("➕ CARGAR CAMIÓN", LINK_FORM, use_container_width=True)

    # 5. MOSTRAR TARJETAS
    if not df.empty:
        # Filtro de búsqueda
        if search:
            df = df[df['destino'].str.contains(search, case=False, na=False) | 
                    df['origen'].str.contains(search, case=False, na=False)]

        # Mostramos los resultados (el más nuevo arriba)
        if not df.empty:
            for _, row in df.iloc[::-1].iterrows():
                # Limpieza del teléfono
                tel_limpio = "".join(filter(str.isdigit, str(row['tel'])))
                
                # Mensaje personalizado
                mensaje = f"Hola! Vi tu camión {row['equipo']} de {row['origen']} a {row['destino']} en Retorno Match. ¿Tenés lugar?"
                link_wa = f"https://wa.me/{tel_limpio}?text={urllib.parse.quote(mensaje)}"
                
                # HTML de la tarjeta (Diseño Lindo)
                st.markdown(f"""
                <div class="camion-card">
                    <div class="card-content">
                        <h3>📍 {str(row['origen']).title()} ➝ {str(row['destino']).title()}</h3>
                        <p>🚛 <b>Equipo:</b> {str(row['equipo']).title()}</p>
                        <p style="font-size: 12px; color: #999; margin-top: 5px;">📅 Publicado: {row['fecha']}</p>
                    </div>
                    <div>
                        <a href="{link_wa}" target="_blank" class="btn-wa">✆ CONTACTAR</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:white; padding: 20px;'>No se encontraron coincidencias para tu búsqueda.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:white;'>Aún no hay camiones cargados hoy.</h3>", unsafe_allow_html=True)

except Exception as e:
    # Mensaje discreto si hay error de conexión
    st.markdown(f"<div style='text-align:center; color:orange;'>Actualizando base de datos... ({str(e)})</div>", unsafe_allow_html=True)

st.markdown("<br><br><p style='text-align:center; color:rgba(255,255,255,0.3); font-size:12px;'>San Jorge 2026</p>", unsafe_allow_html=True)
