import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. EL ID DE TU EXCEL (Verificado de tu imagen)
ID_EXCEL = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/export?format=csv&gid=0"

# 3. DISEÑO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .card { 
        background: white; padding: 20px; border-radius: 10px; 
        border-left: 8px solid #2ecc71; margin-bottom: 20px; 
    }
    .card h3, .card p { color: #1a1a1a !important; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# 4. CARGAR Y MOSTRAR DATOS
try:
    # Leemos el archivo
    df = pd.read_csv(URL_CSV)
    
    # Limpiamos nombres de columnas para que coincidan con el Excel
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty:
        st.success("✅ CONECTADO AL EXCEL")
        
        # Filtramos filas que tengan algo en 'origen'
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
                st.markdown(f'<a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:8px; font-weight:bold; margin-top:-15px; margin-bottom:20px;">📲 CONTACTAR</div></a>', unsafe_allow_html=True)
    else:
        st.warning("El Excel está conectado pero no tiene datos.")

except Exception as e:
    st.error(f"Error de lectura: {e}")

# 5. BOTÓN REFRESCAR
if st.button("🔄 ACTUALIZAR DATOS"):
    st.cache_data.clear()
    st.rerun()
