import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# ID de tu planilla
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"

# Conexión directa a la pestaña 'cargas' por nombre
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=cargas"

# --- PANEL DE DIAGNÓSTICO ---
st.write("### 🔧 Estado de los Datos")
try:
    # Leemos el Excel
    df = pd.read_csv(URL)
    
    # Limpiamos títulos: quitamos espacios y pasamos a minúscula
    df.columns = df.columns.str.strip().str.lower()
    
    if df.empty:
        st.warning("⚠️ El Excel está conectado pero no tiene datos en las filas. Agregá una carga en la fila 2.")
    else:
        st.success(f"✅ Conectado. Se encontraron {len(df)} filas.")
        # Esto te permite ver qué está leyendo la App realmente
        with st.expander("Ver tabla cruda del Excel"):
            st.dataframe(df)
except Exception as e:
    st.error(f"❌ Error de conexión: {e}")
    st.info("Asegurate de que la pestaña del Excel se llame exactamente 'cargas'.")
    st.stop()

st.divider()

# --- INTERFAZ VISUAL ---
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# Verificamos si existen las columnas necesarias
if 'origen' in df.columns and 'item' in df.columns:
    
    # Buscador por Origen
    opciones = ["Todos"] + sorted(df['origen'].astype(str).unique().tolist())
    filtro = st.selectbox("🔍 ¿Desde dónde buscás carga?", opciones)

    for index, row in df.iterrows():
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
            # Limpiamos el número de teléfono por si viene con decimales
            tel = str(row['tel']).split('.')[0].replace(" ", "")
            msg = urllib.parse.quote(f"Hola! Vi la carga de {row['item']} en {row['origen']} en la App.")
            link = f"https://wa.me/549{tel}?text={msg}"
            
            st.markdown(f'''
                <a href="{link}" target="_blank" style="text-decoration:none;">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:20px;">
                        📲 CONTACTAR DUEÑO
                    </button>
                </a>
            ''', unsafe_allow_html=True)
else:
    st.error("⚠️ ERROR DE COLUMNAS")
    st.write("El código busca 'origen', 'item', 'pago' y 'tel'. Revisá que los nombres en el Excel sean iguales.")
