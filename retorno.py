import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN CON TU EXCEL ---
URL_DATOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# --- ESTILOS ---
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    .card { 
        background: white; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 8px solid #2ecc71; 
        margin-bottom: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .card b, .card p, .card h3 { color: #2c3e50 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1);
        border-radius: 5px;
        color: white;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
try:
    df = pd.read_csv(URL_DATOS).dropna(how='all')
    df.columns = df.columns.str.strip().str.lower()
except Exception as e:
    st.error(f"Error conectando con el Excel: {e}")
    st.stop()

# --- PESTAÑAS ---
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 CAMIONES"])

# --- 1. BUSCAR ---
with t1:
    if 'origen' in df.columns:
        opciones = ["Todos"] + sorted(df['origen'].astype(str).unique().tolist())
        filtro = st.selectbox("¿Desde dónde buscás?", opciones)
        
        for _, r in df.iterrows():
            if filtro == "Todos" or str(r['origen']) == filtro:
                st.markdown(f"""
                <div class='card'>
                    <h3>📍 {r['origen']} → San Jorge</h3>
                    <p>📦 <b>Carga:</b> {r['item']}</p>
                    <p>💰 <b>Pago:</b> ${r['pago']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                tel = str(r['tel']).split('.')[0].replace(" ", "").replace("-", "")
                msg = urllib.parse.quote(f"Hola! Vi tu carga de {r['item']} en {r['origen']}. ¿Sigue disponible?")
                st.markdown(f'<a href="https://wa.me/549{tel}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:8px; font-weight:bold; margin-top:-10px; margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles.")

# --- 2. PUBLICAR ---
with t2:
    st.markdown("### Publicar Nueva Carga")
