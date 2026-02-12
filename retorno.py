import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH | Logística", page_icon="🚛", layout="centered")

# --- DISEÑO AVANZADO ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    .main-title {
        color: #FFFFFF;
        text-align: center;
        font-size: 40px;
        font-weight: 900;
        text-shadow: 3px 3px 10px #000000;
        margin-bottom: 5px;
    }

    .sub-title {
        color: #FFD700;
        text-align: center;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .viaje-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 15px;
        border-left: 12px solid #FFD700;
        margin-bottom: 20px;
        box-shadow: 0px 8px 15px rgba(0,0,0,0.4);
    }

    .city-text { color: #1a1a1a; font-size: 24px; font-weight: 800; margin: 0; }
    .item-text { color: #555; font-size: 18px; font-weight: 600; margin-bottom: 10px; }
    .price-tag { 
        background-color: #e8f5e9; 
        color: #2e7d32; 
        padding: 5px 15px; 
        border-radius: 8px; 
        font-weight: 800; 
        font-size: 20px;
        display: inline-block;
    }

    .whatsapp-btn {
        display: block;
        text-align: center;
        background-color: #25D366;
        color: white !important;
        padding: 12px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        margin-top: 15px;
        transition: 0.3s;
    }
    .whatsapp-btn:hover { background-color: #128C7E; transform: scale(1.02); }

    .stTextInput>div>div>input {
        border-radius: 25px;
        padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🚛 RETORNO MATCH</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Buscador de Cargas en Tiempo Real</p>', unsafe_allow_html=True)

# Conexión al Sheets
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

# Buscador
search = st.text_input("", placeholder="🔍 Buscar por origen (ej: San Jorge, Rosario...)")

try:
    df = pd.read_csv(URL)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Filtrar si hay búsqueda
    if search:
        df = df[df['origen'].str.contains(search, case=False, na=False)]

    if not df.empty:
        for _, row in df.iloc[::-1].iterrows():
            if pd.notna(row['origen']):
                # Crear link de WhatsApp automático
                tel_limpio = str(row['tel']).replace(".0", "").replace(" ", "").replace("+", "")
                msg = urllib.parse.quote(f"Hola, vi el viaje desde {row['origen']} por {row['item']} en Retorno Match. ¿Sigue disponible?")
                ws_link = f"https://wa.me/{tel_limpio}?text={msg}"

                st.markdown(f"""
                <div class="viaje-card">
                    <p class="city-text">📍 {str(row['origen']).upper()}</p>
                    <p class="item-text">📦 CARGA: {str(row['item']).upper()}</p>
                    <div class="price-tag">💰 ${row['pago']}</div>
                    <a href="{ws_link}" target="_blank" class="whatsapp-btn">
                        💬 CONTACTAR POR WHATSAPP
                    </a>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No se encontraron viajes con ese origen.")

except Exception as e:
    st.error("Sincronizando con la base de datos...")

if st.button("🔄 REFRESCAR CARTELERA"):
    st.rerun()
