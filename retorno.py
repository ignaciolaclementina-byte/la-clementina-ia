import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# ID de tu planilla (Ya configurado)
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"

# Conexión directa a la pestaña 'cargas'
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

# --- DIAGNÓSTICO EN VIVO (Para ver si llegan los datos) ---
st.write("### 🔧 Panel de Control (Solo vos ves esto)")
try:
    # Leemos el Excel
    df = pd.read_csv(URL)
    
    # TRUCO DE MAGIA: Convertimos todos los títulos a minúscula y borramos espacios
    df.columns = df.columns.str.strip().str.lower()
    
    # Mostramos cuántas cargas encontró
    st.write(f"✅ Conectado. Cargas encontradas: {len(df)}")
    st.dataframe(df) # Esto muestra la tabla cruda
except Exception as e:
    st.error(f"❌ Error crítico: {e}")
    st.stop()

st.divider()

# --- LA APP VISUAL ---
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# Verificamos si están las columnas clave (origen e item)
if 'origen' in df.columns and 'item' in df.columns:
    
    # Buscador
    lugares = ["Todos"] + sorted(df['origen'].astype(str).unique().tolist())
    filtro = st.selectbox("🔍 ¿Dónde estás buscando?", lugares)

    for index, row in df.iterrows():
        # Filtro
        if filtro == "Todos" or str(row['origen']) == filtro:
            
            # Tarjeta de Carga
            st.markdown(f"""
            <div style="background-color:white; padding:15px; border-radius:10px; border-left:8px solid #2ecc71; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color:#2c3e50; margin:0;">📍 {row['origen']}</h3>
                <p style="color:#555; margin:5px 0;">📦 <b>{row['item']}</b></p>
                <p style="color:#27ae60; font-weight:bold;">💰 Pago: ${row['pago']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón WhatsApp
            tel = str(row['tel']).split('.')[0] # Sacamos decimales (.0)
            msg = urllib.parse.quote(f"Hola! Vi la carga de {row['item']} en {row['origen']}.")
            link = f"https://wa.me/549{tel}?text={msg}"
            
            st.markdown(f'''
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:20px;">
                        📲 CONTACTAR
                    </button>
                </a>
            ''', unsafe_allow_html=True)

else:
    st.error("⚠️ PROBLEMA DE TÍTULOS")
    st.warning("Tu Excel no tiene las columnas 'origen' o 'item'. Mirá la tabla de arriba para ver cómo se llaman ahora.")
