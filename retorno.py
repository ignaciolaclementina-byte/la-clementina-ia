import streamlit as st
import pandas as pd
import urllib.parse

st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# TU LINK (Convertido a CSV)
URL_DATOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSLxlHXfxe4BKqlpm1xYZ8yKhrd2vH1mRDNWRNDnmg1zgt6kYlqnobYHkMS_LjfwlQM18PmCCVZzLzm/pub?gid=0&single=true&output=csv"

# Estilo
st.markdown("""
    <style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); background-size: cover; }
    .card { background: white; padding: 15px; border-radius: 10px; border-left: 8px solid #2ecc71; margin-bottom: 15px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .card b, .card p, .card h3 { color: #2c3e50 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

try:
    # Leemos el Excel
    df = pd.read_csv(URL_DATOS)
    
    # LIMPIEZA TOTAL: Pasamos todo a minúsculas para que no falle
    df.columns = df.columns.str.strip().str.lower()
    
    # Intentamos encontrar las columnas aunque tengan nombres un poco distintos
    col_origen = [c for c in df.columns if 'ori' in c][0]
    col_item = [c for c in df.columns if 'item' in c or 'merc' in c or 'que' in c][0]
    col_pago = [c for c in df.columns if 'pago' in c or 'valor' in c or 'precio' in c][0]
    col_tel = [c for c in df.columns if 'tel' in c or 'cel' in c or 'cont' in c][0]

    if df.empty:
        st.warning("⚠️ El Excel está conectado pero no tiene datos cargados.")
    else:
        for _, r in df.iterrows():
            # Mostramos la tarjeta con los datos encontrados
            st.markdown(f"""
            <div class='card'>
                <h3>📍 {r[col_origen]} → San Jorge</h3>
                <p>📦 <b>Carga:</b> {r[col_item]}</p>
                <p>💰 <b>Pago:</b> ${r[col_pago]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botón WhatsApp
            tel_sucio = str(r[col_tel]).split('.')[0].replace(" ", "").replace("-", "")
            msg = urllib.parse.quote(f"Hola! Vi tu carga de {r[col_item]} en {r[col_origen]}. ¿Sigue disponible?")
            st.markdown(f'<a href="https://wa.me/549{tel_sucio}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; text-align:center; padding:12px; border-radius:8px; font-weight:bold; margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ HAY UN PROBLEMA EN EL EXCEL")
    st.info("Asegurate de que la primera fila del Excel tenga los títulos: origen, item, pago, tel")
    st.write("Error para el técnico:", e)
