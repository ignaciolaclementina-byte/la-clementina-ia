import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. ID CORREGIDO (CON LA "S" MAYÚSCULA AL FINAL)
ID_CORRECTO = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS"
URL = f"https://docs.google.com/spreadsheets/d/{ID_CORRECTO}/export?format=csv&gid=0"

# 3. ESTILO PARA QUE SE VEA BIEN
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .card { 
        background: white; padding: 20px; border-radius: 10px; 
        border-left: 10px solid #2ecc71; margin-bottom: 20px; 
    }
    .card h3, .card p { color: #1a1a1a !important; margin: 5px 0; font-family: sans-serif; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. CARGA DIRECTA SIN CACHÉ PARA QUE NO FALLE
try:
    df = pd.read_csv(URL)
    # Limpiamos nombres de columnas
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty:
        st.success("✅ CONECTADO AL EXCEL")
        # Filtramos filas que tengan origen
        viajes = df.dropna(subset=['origen'])
        
        for _, r in viajes.iterrows():
            st.markdown(f"""
            <div class='card'>
                <h3>📍 ORIGEN: {str(r['origen']).upper()}</h3>
                <p><b>📦 CARGA:</b> {r.get('item', '-')}</p>
                <p><b>💰 PAGO:</b> ${r.get('pago', '-')}</p>
                <p><b>📲 TEL:</b> {r.get('tel', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de WhatsApp
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "").replace("+", "")
            if tel and tel != 'nan':
                st.markdown(f'<a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:8px; font-weight:bold; margin-top:-15px; margin-bottom:20px;">📲 CONTACTAR POR WHATSAPP</div></a>', unsafe_allow_html=True)
    else:
        st.warning("El Excel está conectado pero parece estar vacío.")

except Exception as e:
    st.error("Error de conexión. Por favor, revisá que el Excel sea público.")
    st.info(f"ID utilizado: {ID_CORRECTO}")

# 5. BOTÓN REFRESCAR
if st.button("🔄 ACTUALIZAR DATOS"):
    st.cache_data.clear()
    st.rerun()
