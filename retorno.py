import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. TU LINK DE PUBLICACIÓN DIRECTO (Copiado de tu imagen 1b89a2)
URL_FINAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?output=csv"

# 3. ESTILO VISUAL PROFESIONAL
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .viaje-card { 
        background: white; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 10px solid #2ecc71;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .viaje-card h3 { color: #2c3e50 !important; margin-top: 0; font-size: 22px; }
    .viaje-card p { color: #34495e !important; margin: 8px 0; font-size: 18px; }
    .btn-ws {
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        font-weight: bold;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 4. CARGA DE DATOS SIN CACHÉ (PARA RESPUESTA INMEDIATA)
try:
    # Leemos el CSV que generaste al publicar en la web
    df = pd.read_csv(URL_FINAL)
    
    # Normalizamos los nombres de las columnas (quitamos espacios y pasamos a minúscula)
    df.columns = df.columns.str.strip().str.lower()
    
    # Verificamos si hay datos
    if not df.empty:
        # Filtramos filas donde el origen no esté vacío
        viajes = df.dropna(subset=['origen'])
        
        if not viajes.empty:
            for _, r in viajes.iterrows():
                # Formateamos el teléfono para el link de WhatsApp
                tel_limpio = str(r.get('tel', '')).split('.')[0].replace(" ", "").replace("+", "")
                
                # Creamos la tarjeta del viaje
                st.markdown(f"""
                <div class='viaje-card'>
                    <h3>📍 {str(r['origen']).upper()}</h3>
                    <p>📦 <b>Carga:</b> {r.get('item', '-')}</p>
                    <p>💰 <b>Pago:</b> ${r.get('pago', '-')}</p>
                    <p>📲 <b>WhatsApp:</b> {r.get('tel', '-')}</p>
                    <a class='btn-ws' href='https://wa.me/549{tel_limpio}' target='_blank'>ENVIAR WHATSAPP</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Conectado, pero no hay viajes cargados en el Excel.")
    else:
        st.error("El archivo publicado está vacío.")

except Exception as e:
    st.error("Error al leer el link de publicación.")
    st.info("Asegurate de que el Excel siga publicado en la web como .csv")

# 5. BOTÓN REFRESCAR
if st.button("🔄 ACTUALIZAR LISTADO"):
    st.rerun()
