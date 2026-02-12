import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

# Diseño con Sidebar y Estilos
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid #2ecc71; color: black; }
    .instrucciones { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; color: white; border: 1px solid #2ecc71; }
    .stButton>button { background-color: #2ecc71; color: white; font-weight: bold; width: 100%; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN
URL_EXCEL = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. BARRA LATERAL (GUÍA DE USO)
with st.sidebar:
    st.markdown("<h2 style='color: #2ecc71;'>📖 GUÍA RÁPIDA</h2>", unsafe_allow_html=True)
    st.markdown("""
    **Para Camioneros:**
    1. Andá a **PUBLICAR**.
    2. Poné dónde estás y a dónde vas.
    3. ¡Esperá el llamado del dador!
    
    **Para Dadores de Carga:**
    1. Buscá en la lista un camión cerca.
    2. O publicá tu carga en **PUBLICAR**.
    
    *Cualquier duda, tocá el botón de WhatsApp abajo.*
    """)
    st.write("---")
    st.markdown("[📲 Soporte Técnico](https://wa.me/5493406649346)")

# 4. CUERPO PRINCIPAL
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR"])

with tab1:
    try:
        df = conn.read(spreadsheet=URL_EXCEL, ttl=0)
        df = df.dropna(subset=[df.columns[0]])
        
        busqueda = st.text_input("📍 ¿A dónde buscás viaje?", "").lower()
        
        for _, r in df.iterrows():
            if busqueda in str(r.iloc[0]).lower():
                st.markdown(f"""
                <div class="card">
                    <h3>📍 {str(r.iloc[0]).upper()}</h3>
                    <p>📦 <b>Detalle:</b> {r.iloc[1]}</p>
                    <p>💰 <b>Tarifa:</b> {r.get('pago', '-')}</p>
                    <a href="https://wa.me/549{str(r.iloc[3]).split('.')[0]}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:8px; text-decoration:none; display:inline-block; font-weight:bold; margin-top:10px;">📲 CONTACTAR</a>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.info("Buscando viajes disponibles...")

with tab2:
    st.markdown("<div style='background: white; padding: 25px; border-radius: 15px; color: black;'>", unsafe_allow_html=True)
    st.subheader("📝 Nueva Publicación")
    
    with st.form("form_nuevo", clear_on_submit=True):
        origen = st.text_input("Ciudad / Origen")
        detalle = st.text_input("Detalle (Ej: Maíz / Camión Térmico)")
        pago = st.text_input("Pago ofrecido / Tarifa")
        tel = st.text_input("WhatsApp (Solo números)")
        
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA")
        
        if enviar:
            if origen and tel:
                df_actual = conn.read(spreadsheet=URL_EXCEL, ttl=0)
                nueva_data = pd.DataFrame([{"origen": origen, "item": detalle, "pago": pago, "tel": tel}])
                df_final = pd.concat([df_actual, nueva_data], ignore_index=True)
                conn.update(spreadsheet=URL_EXCEL, data=df_final)
                st.success("✅ ¡Publicado con éxito!")
                st.balloons()
            else:
                st.error("Completá origen y teléfono.")
    st.markdown("</div>", unsafe_allow_html=True)
