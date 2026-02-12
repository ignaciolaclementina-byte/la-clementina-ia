import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | Logística", page_icon="🚛", layout="wide")

# 2. ESTILO DE INTERFAZ PREMIUM
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-header { text-align: center; padding: 20px 0; }
    .main-header h1 { color: white; font-size: 50px; font-weight: 900; margin-bottom: 0; text-shadow: 2px 2px 10px black; }
    .main-header p { color: #00FF41; font-size: 20px; font-weight: bold; text-transform: uppercase; }

    /* Tarjetas de Camiones */
    .camion-card {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 0;
        margin-bottom: 25px;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.5);
        overflow: hidden;
    }
    
    .card-header {
        background: #f8f9fa;
        padding: 15px 25px;
        border-bottom: 1px solid #eee;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .route-text { font-size: 22px; font-weight: 800; color: #1a1a1a; }
    .tag-dispo { background: #00FF41; color: black; padding: 4px 12px; border-radius: 50px; font-size: 12px; font-weight: 800; }

    .card-body { padding: 20px 25px; }
    .label { color: #888; font-size: 12px; font-weight: bold; text-transform: uppercase; }
    .value { color: #333; font-size: 18px; font-weight: 700; margin-bottom: 10px; }

    .btn-wa {
        background: #25D366;
        color: white !important;
        text-align: center;
        padding: 15px;
        display: block;
        text-decoration: none;
        font-weight: 900;
        font-size: 18px;
        border-radius: 0 0 15px 15px;
        transition: 0.3s;
    }
    .btn-wa:hover { background: #128C7E; }

    /* Estilo del buscador */
    .stTextInput input {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 50px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("""
    <div class="main-header">
        <h1>RETORNO MATCH</h1>
        <p>Disponibilidad de Camiones en Vacío</p>
    </div>
""", unsafe_allow_html=True)

# 4. NAVEGACIÓN
col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    st.button("🔍 BUSCAR RETORNOS", use_container_width=True, type="primary")
with col_nav2:
    if st.button("🔄 ACTUALIZAR LISTADO", use_container_width=True):
        st.rerun()
with col_nav3:
    # Link del formulario que me pasaste
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScWcPChu8-wqWSijj9IoA5ES6CunJOJTirhPvqXKHkl_sy9MA/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

st.write("---")

# 5. BUSCADOR
search = st.text_input("", placeholder="🔍 ¿A qué ciudad necesitás mandar carga? (Ej: Rosario, Córdoba...)")

# 6. CARGA DE DATOS DESDE LAS RESPUESTAS DEL FORMULARIO
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%201"

try:
    df = pd.read_csv(URL)
    
    # Ajustamos las columnas según el orden de Google Forms:
    # [Marca temporal, Ubicación Actual, Destino del Retorno, Tipo de Equipo, WhatsApp de Contacto]
    df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
    
    # Filtrado por búsqueda
    if search:
        df = df[df['destino'].str.contains(search, case=False, na=False) | 
                df['origen'].str.contains(search, case=False, na=False)]

    if not df.empty:
        # Mostramos los últimos cargados arriba (orden inverso)
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Limpiar el teléfono por si viene con espacios o .0
                tel_final = str(row['tel']).split('.')[0].replace(" ", "").replace("+", "")
                
                # Mensaje automático para el transportista
                msg = urllib.parse.quote(f"Hola! Vi en Retorno Match que tenés el camión disponible desde {row['origen']} hacia {row['destino']}. ¿Todavía lo tenés vacío?")
                wa_link = f"https://wa.me/{tel_final}?text={msg}"
                
                st.markdown(f"""
                <div class="camion-card">
                    <div class="card-header">
                        <span class="route-text">📍 {str(row['origen']).upper()} ⮕ 🏁 {str(row['destino']).upper()}</span>
                        <span class="tag-dispo">DISPONIBLE</span>
                    </div>
                    <div class="card-body">
                        <div style="display: flex; justify-content: space-between;">
                            <div>
                                <p class="label">Equipo / Camión</p>
                                <p class="value">🚛 {row['equipo']}</p>
                            </div>
                            <div style="text-align: right;">
                                <p class="label">Publicado</p>
                                <p class="value" style="font-size: 14px;">{row['fecha']}</p>
                            </div>
                        </div>
                    </div>
                    <a href="{wa_link}" target="_blank" class="btn-wa">
                        📱 CONTACTAR AL TRANSPORTISTA
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:white; text-align:center;'>No hay camiones vacíos reportados en esta ruta por el momento.</p>", unsafe_allow_html=True)

except Exception as e:
    st.error("Conectando con la base de datos de transportistas...")

st.markdown("<br><p style='text-align:center; color: #666;'>Logística Inteligente - San Jorge, Santa Fe | 2026</p>", unsafe_allow_html=True)
