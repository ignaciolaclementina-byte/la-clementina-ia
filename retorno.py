import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. TU LINK DE EXCEL (Verificado de tu imagen)
# Usamos el link de exportación que nunca falla con archivos públicos
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# 3. ESTILO (Para que se vea como querés)
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    h1, h3, p, [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #2ecc71; 
        margin-bottom: 20px; 
    }
    .card h3, .card p { color: #2c3e50 !important; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. CARGAR DATOS
@st.cache_data(ttl=60) # Actualiza cada 1 minuto
def cargar_datos(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip().str.lower()
        return df
    except Exception as e:
        return None

df = cargar_datos(URL)

# 5. PESTAÑAS
t1, t2, t3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR", "🚛 CAMIONES"])

with t1:
    if df is not None:
        # Filtramos filas que tengan al menos el origen
        datos = df.dropna(subset=['origen'])
        if not datos.empty:
            for _, r in datos.iterrows():
                st.markdown(f"""
                <div class='card'>
                    <h3>📍 {str(r['origen']).upper()}</h3>
                    <p>📦 <b>Carga:</b> {r.get('item', 'Carga')}</p>
                    <p>💰 <b>Pago:</b> ${r.get('pago', '-')}</p>
                    <p>📲 <b>WhatsApp:</b> {r.get('tel', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón de contacto
                tel = str(r.get('tel', '')).split('.')[0].replace(" ", "").replace("+", "")
                if tel:
                    st.markdown(f'<a href="https://wa.me/{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-bottom:20px;">📲 ENVIAR WHATSAPP</div></a>', unsafe_allow_html=True)
        else:
            st.info("Conectado al Excel, pero no hay viajes escritos debajo de los títulos.")
    else:
        st.error("Esperando conexión con Google Sheets... (Refrescá en 10 segundos)")

with t2:
    st.write("Sección para publicar.")

with t3:
    st.write("Sección de camiones.")
