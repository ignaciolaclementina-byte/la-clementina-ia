import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH | Logística", page_icon="🚛", layout="wide")

# --- DISEÑO TIPO PORTAL PROFESIONAL (Basado en tu imagen anterior) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-header {
        text-align: center;
        padding: 20px;
    }

    .title-text {
        color: white;
        font-size: 45px;
        font-weight: 900;
        text-transform: uppercase;
        margin-bottom: 0px;
        text-shadow: 2px 2px 15px rgba(0,0,0,1);
    }

    /* Menú de pestañas estilo botones */
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 30px;
    }

    /* Tarjetas de camiones */
    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 10px solid #28a745;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }

    .status-badge {
        background: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }

    .wa-button {
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        display: block;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
        font-size: 18px;
    }

    .hero-section {
        text-align: center;
        color: white;
        padding: 40px 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown('<div class="main-header"><p class="title-text">🚛 RETORNO MATCH</p></div>', unsafe_allow_html=True)

# --- NAVEGACIÓN (Simulada con columnas de Streamlit para que sea funcional) ---
col_nav1, col_nav2, col_nav3 = st.columns([1,1,1])
with col_nav1:
    btn_cargas = st.button("🔍 BUSCAR CARGA", use_container_width=True)
with col_nav2:
    btn_camiones = st.button("🚛 CAMIONES DISPONIBLES", use_container_width=True)
with col_nav3:
    st.link_button("➕ PUBLICAR", "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit", use_container_width=True)

st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.2)'>", unsafe_allow_html=True)

# --- LÓGICA DE CONTENIDO ---
st.markdown('<div class="hero-section"><h2>¿Sos Cliente o Transportista?</h2><p>Encontrá el match perfecto para aprovechar el viaje vacío.</p></div>', unsafe_allow_html=True)

# Conexión al Sheets
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]

    # Buscador principal
    search = st.text_input("", placeholder="🔍 Escribí el destino o ciudad para filtrar camiones en vacío...")

    if search:
        df = df[df['item'].str.contains(search, case=False, na=False) | df['origen'].str.contains(search, case=False, na=False)]

    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Datos para WhatsApp
                tel = str(row['tel']).replace(".0", "")
                msg = urllib.parse.quote(f"Hola! Vi tu camión en Retorno Match. ¿Tenes disponibilidad desde {row['origen']} hacia {row['item']}?")
                
                st.markdown(f"""
                <div class="card">
                    <span class="status-badge">CAMIÓN DISPONIBLE</span>
                    <h2 style="color: #1a1a1a; margin-top:10px;">📍 {str(row['origen']).upper()} ➡️ {str(row['item']).upper()}</h2>
                    <p style="color: #555;"><strong>EQUIPO:</strong> {row['pago']}</p>
                    <a href="https://wa.me/{tel}?text={msg}" target="_blank" class="wa-button">
                        ✅ CONTACTAR TRANSPORTISTA
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay camiones reportados en esta zona por ahora.")

except Exception as e:
    st.error("Conectando con la central de cargas...")

st.markdown("<br><center><button style='border-radius:20px; padding:10px; background:#1E1E1E; color:white; border:none;'>🔄 ACTUALIZAR APP</button></center>", unsafe_allow_html=True)
