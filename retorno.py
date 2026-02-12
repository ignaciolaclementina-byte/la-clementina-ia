import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH | Logística Inteligente", page_icon="🚛", layout="wide")

# --- INTERFAZ PREMIUM ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.75)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Encabezado */
    .hero-text {
        text-align: center;
        color: white;
        padding: 20px 0;
    }
    .hero-text h1 { font-size: 50px; font-weight: 900; margin-bottom: 0; text-shadow: 2px 2px 10px black; }
    .hero-text p { font-size: 20px; color: #00FF41; font-weight: bold; }

    /* Tarjetas de Camiones (Mejoradas) */
    .card-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        border-top: 5px solid #28a745;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.4);
        color: #333;
    }

    .route-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }

    .badge-dispo {
        background: #28a745;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }

    .data-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }

    .data-label { color: #888; font-size: 14px; text-transform: uppercase; font-weight: bold; }
    .data-value { color: #1a1a1a; font-size: 18px; font-weight: 700; }

    /* Botón de WhatsApp estilizado */
    .btn-contact {
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 15px;
        border-radius: 8px;
        display: block;
        text-decoration: none;
        font-weight: bold;
        font-size: 18px;
        margin-top: 20px;
        box-shadow: 0px 4px 10px rgba(37, 211, 102, 0.3);
    }
    
    /* Ajustes de inputs */
    .stTextInput>div>div>input {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 50px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="hero-text">
        <h1>RETORNO MATCH</h1>
        <p>CONECTANDO CAMIONES VACÍOS CON CARGAS DISPONIBLES</p>
    </div>
""", unsafe_allow_html=True)

# --- BOTONES DE ACCIÓN ---
col1, col2, col3 = st.columns(3)
with col1:
    st.button("🔍 BUSCAR CARGA", use_container_width=True)
with col2:
    st.button("🚛 CAMIONES DISPONIBLES", use_container_width=True, type="primary")
with col3:
    st.link_button("➕ PUBLICAR DISPO", "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit", use_container_width=True)

st.write("---")

# --- BUSCADOR ---
search = st.text_input("", placeholder="🔍 Filtrar por destino o equipo (ej: Rosario, Batea, Sider...)")

# --- CARGA DE DATOS ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]

    if search:
        df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                tel = str(row['tel']).replace(".0", "")
                msg = urllib.parse.quote(f"Hola! Vi tu camión en Retorno Match. ¿Tenés disponibilidad desde {row['origen']} hacia {row['item']}?")
                
                st.markdown(f"""
                <div class="card-container">
                    <div class="route-header">
                        <span style="font-size: 22px; font-weight: 900;">📍 {str(row['origen']).upper()} ⮕ {str(row['item']).upper()}</span>
                        <span class="badge-dispo">RETORNO DISPONIBLE</span>
                    </div>
                    <div class="data-row">
                        <div>
                            <p class="data-label">Equipo / Observaciones</p>
                            <p class="data-value">🚛 {row['pago']}</p>
                        </div>
                        <div style="text-align: right;">
                            <p class="data-label">Publicado</p>
                            <p class="data-value">Hoy</p>
                        </div>
                    </div>
                    <a href="https://wa.me/{tel}?text={msg}" target="_blank" class="btn-contact">
                        📱 CONTACTAR AL CHOFER
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Buscando retornos disponibles en la red...")

except Exception as e:
    st.error("Conexión activa con Google Sheets.")

st.caption("Central de Logística San Jorge | 2026")
