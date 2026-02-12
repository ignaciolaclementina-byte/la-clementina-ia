import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. CONEXIÓN DIRECTA (ID y GID de tu imagen)
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Este link descarga directamente la pestaña 'cargas' (gid=0)
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# 3. DISEÑO DE LA APP
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    h1, h2, h3, p, label, .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #2ecc71; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.5);
    }
    .card h3, .card p, .card b { color: #2c3e50 !important; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. CARGAR LOS DATOS
def cargar_datos():
    try:
        # Cargamos el CSV y limpiamos nombres de columnas
        df = pd.read_csv(URL_CARGAS)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except:
        return pd.DataFrame()

df = cargar_datos()

# 5. MOSTRAR CONTENIDO
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 CAMIONES"])

with t1:
    if not df.empty and 'origen' in df.columns:
        # Quitamos filas vacías
        datos = df.dropna(subset=['origen'])
        if not datos.empty:
            for _, r in datos.iterrows():
                st.markdown(f"""
                <div class='card'>
                    <h3>📍 {str(r['origen']).upper()}</h3>
                    <p>📦 <b>Carga:</b> {r.get('item', 'Carga General')}</p>
                    <p>💰 <b>Pago:</b> ${r.get('pago', 'A convenir')}</p>
                    <p>📲 <b>Tel:</b> {r.get('tel', 'Sin número')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón de WhatsApp directo
                tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
                if tel:
                    st.markdown(f'<a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-top:-10px; margin-bottom:25px;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)
        else:
            st.warning("El Excel está conectado pero no hay viajes escritos debajo de los títulos.")
    else:
        st.error("No se pudieron leer los datos. Revisá que el Excel sea público.")

with t2:
    st.markdown("### 📤 Próximamente")
    st.write("Aquí podrás publicar tus cargas.")

with t3:
    st.write("Sección de camiones disponibles.")
