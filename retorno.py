import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH | Portal de Disponibilidad", page_icon="🚛", layout="wide")

# --- ESTILO DE INTERFAZ PROFESIONAL ---
st.markdown("""
    <style>
    /* Fondo de depósito logístico profesional */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Header Principal */
    .main-header { text-align: center; padding: 30px 0; }
    .main-header h1 { color: white; font-size: 55px; font-weight: 900; margin-bottom: 5px; }
    .main-header p { color: #00FF41; font-size: 22px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; }

    /* Tarjetas de Camiones Disponibles */
    .camion-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 0;
        margin-bottom: 25px;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.5);
        overflow: hidden;
        border: 1px solid #e0e0e0;
    }
    
    .card-header {
        background: #f8f9fa;
        padding: 15px 25px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .card-body { padding: 25px; }

    .route-text { font-size: 24px; font-weight: 800; color: #1a1a1a; }
    .route-arrow { color: #007bff; padding: 0 10px; }

    .tag-dispo {
        background: #00FF41;
        color: #000;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 800;
    }

    .info-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 15px;
    }

    .label { color: #888; font-size: 13px; font-weight: bold; text-transform: uppercase; }
    .value { color: #333; font-size: 18px; font-weight: 700; }

    /* Botón de Acción para Empresas */
    .btn-contratar {
        background: #25D366;
        color: white !important;
        text-align: center;
        padding: 15px;
        display: block;
        text-decoration: none;
        font-weight: 900;
        font-size: 18px;
        transition: 0.3s;
    }
    .btn-contratar:hover { background: #128C7E; }

    /* Estilo del buscador */
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid #444 !important;
        height: 60px;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("""
    <div class="main-header">
        <h1>RETORNO MATCH</h1>
        <p>Logística de Retornos en Tiempo Real</p>
    </div>
""", unsafe_allow_html=True)

# --- NAVEGACIÓN RÁPIDA ---
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button("🚛 VER CAMIONES VACÍOS", use_container_width=True, type="primary"):
        st.rerun()
with col_nav2:
    st.button("📦 VER CARGAS", use_container_width=True)
with col_nav3:
    st.link_button("➕ PUBLICAR DISPONIBILIDAD", "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit", use_container_width=True)

st.write("")

# --- BUSCADOR INTELIGENTE PARA EMPRESAS ---
search = st.text_input("", placeholder="🔍 ¿A dónde necesitás enviar carga? (Ej: Rosario, Córdoba, Buenos Aires...)")

# --- CONEXIÓN Y DATOS ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]

    # Lógica de búsqueda: Filtra por destino del camión (columna 'item')
    if search:
        df = df[df['item'].str.contains(search, case=False, na=False) | df['origen'].str.contains(search, case=False, na=False)]

    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                tel = str(row['tel']).replace(".0", "").replace(" ", "")
                # Mensaje pre-armado para el chofer
                msg = urllib.parse.quote(f"Hola! Vi en Retorno Match que estás volviendo vacío desde {row['origen']} hacia {row['item']}. Tengo una carga para ofrecerte. ¿Te interesa?")
                
                st.markdown(f"""
                <div class="camion-card">
                    <div class="card-header">
                        <span class="route-text">📍 {str(row['origen']).upper()} <span class="route-arrow">⮕</span> 🏁 {str(row['item']).upper()}</span>
                        <span class="tag-dispo">● DISPONIBLE</span>
                    </div>
                    <div class="card-body">
                        <div class="info-grid">
                            <div>
                                <p class="label">Equipo / Camión</p>
                                <p class="value">🚛 {row['pago']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p class="label">Estado de Carga</p>
                                <p class="value" style="color: #28a745;">VACÍO / EN RETORNO</p>
                            </div>
                        </div>
                        <a href="https://wa.me/{tel}?text={msg}" target="_blank" class="btn-contratar">
                            SOLICITAR CARGA PARA ESTE CAMIÓN
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color:white; text-align:center;'>No se encontraron camiones para esta ruta por ahora.</h3>", unsafe_allow_html=True)

except Exception as e:
    st.error("Sincronizando con la red de transportistas...")

st.markdown("<br><p style='text-align:center; color: #666;'>Sistema de Match Logístico - San Jorge 2026</p>", unsafe_allow_html=True)
