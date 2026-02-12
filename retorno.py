import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. ID CORREGIDO (La S final es MAYÚSCULA)
ID_CORRECTO = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS"
URL = f"https://docs.google.com/spreadsheets/d/{ID_CORRECTO}/export?format=csv&gid=0"

# 3. ESTILO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .card { 
        background: white; padding: 20px; border-radius: 10px; 
        border-left: 8px solid #2ecc71; margin-bottom: 15px; 
    }
    .card h3, .card p { color: #1a1a1a !important; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# 4. BOTÓN DE EMERGENCIA
if st.button("🔄 FORZAR ACTUALIZACIÓN"):
    st.cache_data.clear()

# 5. CARGA DIRECTA
try:
    df = pd.read_csv(URL)
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty:
        st.success("✅ ¡CONECTADO!")
        # Solo filas con origen
        viajes = df.dropna(subset=['origen'])
        for _, r in viajes.iterrows():
            st.markdown(f"""
            <div class='card'>
                <h3>📍 {str(r['origen']).upper()}</h3>
                <p><b>📦 Carga:</b> {r.get('item', '-')}</p>
                <p><b>💰 Pago:</b> ${r.get('pago', '-')}</p>
                <p><b>📲 Tel:</b> {r.get('tel', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
            if tel and tel != 'nan':
                st.markdown(f'<a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold; margin-bottom:20px;">💬 WHATSAPP</div></a>', unsafe_allow_html=True)
    else:
        st.warning("Excel conectado, pero está vacío.")
except Exception as e:
    st.error("Error de link. Verificá que el Excel siga en 'Cualquier persona con el enlace'.")
