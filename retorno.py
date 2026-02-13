import streamlit as st
import pandas as pd
import urllib.parse
import time
import requests

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH | San Jorge", page_icon="🚛", layout="wide")

# 2. ESTILO CSS DEFINITIVO (Fondo Fijo + Pestañas)
st.markdown("""
    <style>
    /* FORZAR FONDO EN TODA LA APP */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80');
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* TARJETAS ESTILO PREMIUM */
    .card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .card-camion { border-left: 10px solid #25D366; }
    .card-carga { border-left: 10px solid #3498db; }

    .title-text { font-size: 22px; font-weight: 800; color: #1a1a1a !important; margin: 0; }
    .sub-text { color: #555 !important; font-size: 15px; margin: 5px 0; }

    /* BOTONES */
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .btn-empresa {
        background-color: #3498db;
        color: white !important;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
    }

    /* ESTILO DE LAS PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        font-weight: bold;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #25D366 !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. CABECERA
st.markdown("<h1 style='text-align:center; color:white; font-size: 50px; font-weight: 900; margin-bottom:0;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#25D366; font-size: 18px; font-weight: bold; margin-top:-10px;'>SISTEMA INTEGRAL DE LOGÍSTICA — SAN JORGE</p>", unsafe_allow_html=True)

# 4. PESTAÑAS DE TRABAJO
tab_chofer, tab_empresa = st.tabs(["🚚 BUSCAR CARGA (Para Choferes)", "📦 BUSCAR CAMIÓN (Para Empresas)"])

# --- VISTA PARA CHOFERES (BUSCAN CARGAS DE EMPRESAS) ---
with tab_chofer:
    st.markdown("<h3 style='color:white;'>🏢 Cargas Disponibles</h3>", unsafe_allow_html=True)
    
    # Formulario para que la empresa cargue lo que necesita
    with st.expander("📢 PUBLICAR NECESIDAD DE CARGA (Uso exclusivo Empresas)"):
        with st.form("form_empresa"):
            c1, c2 = st.columns(2)
            with c1:
                e_ori = st.text_input("📍 Origen de la carga")
                e_tipo = st.text_input("📦 Qué mercadería es")
            with c2:
                e_des = st.text_input("🏁 Destino de la carga")
                e_tel = st.text_input("📱 WhatsApp de contacto")
            st.form_submit_button("PUBLICAR CARGA")

    # Ejemplo de cómo se vería una carga publicada por una empresa
    st.markdown("""
        <div class="card card-carga">
            <div>
                <p class="title-text">📍 ROSARIO → SAN JORGE</p>
                <p class="sub-text">📦 <b>CARGA:</b> 15 Pallets (Alimento) | 🏢 <b>EMPRESA:</b> Distribuidora S.J.</p>
            </div>
            <a href="#" class="btn-empresa">ACEPTAR CARGA</a>
        </div>
    """, unsafe_allow_html=True)

# --- VISTA PARA EMPRESAS (BUSCAN CAMIONES VACÍOS) ---
with tab_empresa:
    st.markdown("<h3 style='color:white;'>🚛 Camiones Vacíos Disponibles</h3>", unsafe_allow_html=True)
    
    with st.expander("📝 PUBLICAR MI CAMIÓN (Para Choferes)"):
        with st.form("form_chofer", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                ori = st.text_input("📍 Origen")
                equ = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider"])
            with f2:
                des = st.text_input("🏁 Destino")
                tel = st.text_input("📱 WhatsApp")
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                # Aquí va tu lógica de requests.post al Google Form
                st.success("Publicado correctamente.")

    # CARGA DE DATOS DESDE GOOGLE SHEETS
    SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
    URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%203&t={int(time.time())}"
    
    try:
        df = pd.read_csv(URL)
        df = df.iloc[:, :5]
        df.columns = ['fecha', 'origen', 'destino', 'equipo', 'tel']
        
        for _, row in df.iloc[::-1].iterrows():
            tel_num = "".join(filter(str.isdigit, str(row['tel'])))
            link_wa = f"https://wa.me/{tel_num}?text=Hola!%20Vi%20tu%20camion%20en%20Retorno%20Match"
            
            st.markdown(f"""
                <div class="card card-camion">
                    <div>
                        <p class="title-text">📍 {str(row['origen']).upper()} → {str(row['destino']).upper()}</p>
                        <p class="sub-text">🚛 <b>EQUIPO:</b> {row['equipo']} | 📅 {row['fecha']}</p>
                    </div>
                    <a href="{link_wa}" target="_blank" class="btn-wa">WHATSAPP</a>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("Conectando con la base de datos...")

st.markdown("<br><hr><p style='text-align:center; color:white; opacity:0.6;'>Logística San Jorge 2026</p>", unsafe_allow_html=True)
