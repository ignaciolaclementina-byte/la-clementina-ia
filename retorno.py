import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. EL ID DEFINITIVO (Copiado de tu imagen 1b1d99)
# Revisé letra por letra: es 18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs
ID_EXCEL = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CSV = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/export?format=csv&gid=0"

# 3. DISEÑO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .viaje-card { 
        background: white; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #2ecc71;
        margin-bottom: 15px;
    }
    .viaje-card h3, .viaje-card p { color: #1a1a1a !important; margin: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# 4. LECTURA FORZADA
if st.button("🔄 REFRESCAR CONEXIÓN"):
    st.cache_data.clear()

try:
    # Leemos el CSV directamente sin caché para probar la conexión
    df = pd.read_csv(URL_CSV)
    df.columns = df.columns.str.strip().str.lower()
    
    if not df.empty:
        st.success("✅ CONECTADO AL EXCEL")
        # Filtrar solo filas con datos
        viajes = df.dropna(subset=['origen'])
        
        for _, r in viajes.iterrows():
            st.markdown(f"""
            <div class='viaje-card'>
                <h3>📍 {str(r['origen']).upper()}</h3>
                <p><b>📦 Carga:</b> {r.get('item', '-')}</p>
                <p><b>💰 Pago:</b> ${r.get('pago', '-')}</p>
                <p><b>📲 Tel:</b> {r.get('tel', '-')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón de WhatsApp
            tel = str(r.get('tel', '')).split('.')[0].replace(" ", "")
            if tel and tel != 'nan':
                st.markdown(f'<a href="https://wa.me/549{tel}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold; margin-top:-10px; margin-bottom:20px;">💬 WHATSAPP</div></a>', unsafe_allow_html=True)
    else:
        st.warning("El Excel está conectado pero no veo datos en las filas.")

except Exception as e:
    st.error(f"Error de dirección. El ID del Excel no es correcto o no es público.")
    st.info(f"ID intentado: {ID_EXCEL}")
