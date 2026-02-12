import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; color: white !important; font-weight: bold; }
    .stTabs [aria-selected="true"] { background-color: #2ecc71 !important; border-radius: 5px; }
    
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.4); }
    .card-carga { border-left: 12px solid #2ecc71; }
    .card-camion { border-left: 12px solid #3498db; }
    .card h3, .card p { color: #1a1a1a !important; margin: 5px 0; }
    
    .btn-ws { 
        background: #25D366; color: white !important; text-align: center; 
        padding: 12px; border-radius: 8px; text-decoration: none; 
        display: block; font-weight: bold; margin-top: 10px;
    }
    h1 { color: white !important; text-align: center; text-shadow: 2px 2px 4px #000; }
    </style>
    """, unsafe_allow_html=True)

# 2. LINKS DE CONEXIÓN (Usando tu link de publicación verificado)
# Para leer diferentes pestañas del mismo Excel publicado, usamos el parámetro gid
URL_BASE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"
URL_CARGAS = f"{URL_BASE}&gid=0"          # La primera pestaña (cargas)
URL_CAMIONES = f"{URL_BASE}&gid=1752528761" # Tu ID de la pestaña camiones según tu imagen

def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

# 3. INTERFAZ
st.markdown("<h1>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
tab_cargas, tab_camiones, tab_publicar = st.tabs(["🔍 BUSCAR CARGA", "🚚 CAMIONES DISPONIBLES", "📤 PUBLICAR"])

# --- PESTAÑA CARGAS ---
with tab_cargas:
    df_c = cargar_datos(URL_CARGAS)
    if not df_c.empty and 'origen' in df_c.columns:
        for _, r in df_c.dropna(subset=['origen']).iterrows():
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
            st.markdown(f"""
            <div class='card card-carga'>
                <h3>📍 ORIGEN: {str(r['origen']).upper()}</h3>
                <p><b>📦 CARGA:</b> {r.get('item', '-')}</p>
                <p><b>💰 PAGO:</b> ${r.get('pago', '-')}</p>
                <a class='btn-ws' href='https://wa.me/549{tel}' target='_blank'>💬 CONTACTAR CLIENTE</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Esperando que los clientes publiquen cargas...")

# --- PESTAÑA CAMIONES ---
with tab_camiones:
    df_m = cargar_datos(URL_CAMIONES)
    if not df_m.empty and 'nombre' in df_m.columns:
        for _, r in df_m.dropna(subset=['nombre']).iterrows():
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
            st.markdown(f"""
            <div class='card card-camion'>
                <h3>🚛 {str(r['nombre']).upper()}</h3>
                <p><b>🏗️ UNIDAD:</b> {r.get('unidad', '-')}</p>
                <p><b>📍 UBICACIÓN:</b> {r.get('ubicacion', '-')}</p>
                <p><b>🏁 DESTINO:</b> {r.get('destino', '-')}</p>
                <a class='btn-ws' style='background:#3498db;' href='https://wa.me/549{tel}' target='_blank'>💬 LLAMAR CAMIONERO</a>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No hay camiones reportados en viaje todavía.")

# --- PESTAÑA PUBLICAR ---
with tab_publicar:
    st.markdown("<h2 style='color:white; text-align:center;'>¿Querés aparecer en la lista?</h2>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style='background:rgba(255,255,255,0.1); padding:20px; border-radius:10px; color:white; text-align:center;'>
            <p>Completá tus datos en la planilla y se actualizará en tiempo real.</p>
            <a href="https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS/edit" 
               target="_blank" style="color:#2ecc71; font-weight:bold; text-decoration:none; font-size:20px;">
               📂 ABRIR EXCEL DE CARGAS Y CAMIONES
            </a>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🔄 REFRESCAR APP"):
        st.cache_data.clear()
        st.rerun()
