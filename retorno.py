import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN ---
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
# Usamos gviz para buscar por NOMBRE de pestaña (más seguro)
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- ZONA DE DIAGNÓSTICO (ESTO TE VA A DECIR QUÉ PASA) ---
st.write("---")
st.subheader("🔧 Estado de Conexión")

try:
    df_cargas = pd.read_csv(URL_CARGAS)
    # Normalizamos nombres de columnas (todo a minúscula y sin espacios)
    df_cargas.columns = df_cargas.columns.str.strip().str.lower()
    
    st.success(f"✅ Conexión exitosa con 'cargas'. Filas encontradas: {len(df_cargas)}")
    st.write("Columnas que veo en el Excel:", list(df_cargas.columns))
    
    # Mostramos los datos crudos para que veas si llegan
    with st.expander("Ver datos crudos del Excel"):
        st.dataframe(df_cargas)

except Exception as e:
    st.error(f"❌ Error leyendo pestaña 'cargas': {e}")
    df_cargas = pd.DataFrame()

try:
    df_camiones = pd.read_csv(URL_CAMIONES)
    df_camiones.columns = df_camiones.columns.str.strip().str.lower()
except:
    df_camiones = pd.DataFrame()

st.write("---")

# --- INTERFAZ PRINCIPAL ---
t1, t2 = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR"])

with t1:
    # Verificamos si existen las columnas necesarias
    if 'origen' in df_cargas.columns and 'item' in df_cargas.columns:
        origenes = ["Todos"] + sorted(df_cargas['origen'].astype(str).unique().tolist())
        filtro = st.selectbox("Filtrar por origen", origenes)
        
        hay_resultados = False
        for _, row in df_cargas.iterrows():
            if filtro == "Todos" or str(row['origen']) == filtro:
                hay_resultados = True
                # Estilo de tarjeta
                st.markdown(f"""
                <div style="background:white; padding:15px; border-radius:10px; border-left:5px solid #2ecc71; margin-bottom:10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                    <b style="color:#2c3e50; font-size:18px;">📍 {row['origen']}</b><br>
                    <span style="color:#555;">📦 {row['item']}</span><br>
                    <span style="color:#27ae60; font-weight:bold;">💰 ${row['pago']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón WhatsApp
                tel = str(row['tel']).split('.')[0] # Sacar decimales
                msg = urllib.parse.quote(f"Hola, vi tu carga de {row['item']}.")
                st.markdown(f'<a href="https://wa.me/549{tel}?text={msg}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:8px; border-radius:5px; margin-bottom:15px;">📲 CONTACTAR</button></a>', unsafe_allow_html=True)
        
        if not hay_resultados:
            st.info("No hay cargas para ese filtro.")
            
    else:
        st.error("⚠️ PROBLEMA DE COLUMNAS:")
        st.warning("El Excel NO tiene las columnas 'origen' o 'item'.")
        st.write("Por favor, en tu Excel poné estos títulos exactos en la fila 1:")
        st.code("origen | item | pago | tel")

with t2:
    st.info("Para publicar, enviamos los datos a la central.")
    if st.button("📲 ABRIR WHATSAPP CENTRAL"):
        st.markdown('<meta http-equiv="refresh" content="0; url=https://wa.me/5493406433604">', unsafe_allow_html=True)
