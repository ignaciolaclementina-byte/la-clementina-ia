import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# Diseño Premium
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid #2ecc71; color: black; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
    .stButton>button { background-color: #2ecc71; color: white; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN DIRECTA (Usando el link que me pasaste)
URL_EXCEL = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs/edit?usp=sharing"

# Conectamos con el motor de Google Sheets de Streamlit
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. INTERFAZ
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 BUSCAR DISPONIBLES", "📤 PUBLICAR AHORA"])

with tab1:
    # LECTURA: Trae los datos del Excel al instante
    try:
        df = conn.read(spreadsheet=URL_EXCEL, ttl=0) # ttl=0 para que no use caché
        df = df.dropna(subset=[df.columns[0]]) # Limpia filas vacías
        
        busqueda = st.text_input("📍 Filtrar por ciudad...", "").lower()
        
        for _, r in df.iterrows():
            if busqueda in str(r.iloc[0]).lower():
                st.markdown(f"""
                <div class="card">
                    <h3>📍 {str(r.iloc[0]).upper()}</h3>
                    <p>📦 <b>Detalle:</b> {r.iloc[1]}</p>
                    <p>💰 <b>Pago/Tarifa:</b> {r.iloc[2]}</p>
                    <p>📲 <b>WhatsApp:</b> {r.iloc[3]}</p>
                    <a href="https://wa.me/549{str(r.iloc[3]).split('.')[0]}" target="_blank" style="background:#25D366; color:white; padding:10px; border-radius:8px; text-decoration:none; display:inline-block; font-weight:bold; margin-top:10px;">📲 CONTACTAR</a>
                </div>
                """, unsafe_allow_html=True)
    except:
        st.warning("Cargando datos... Si tarda, verificá los permisos del Excel.")

with tab2:
    # ESCRITURA: Formulario para cargar datos directamente
    st.markdown("<div style='background: white; padding: 25px; border-radius: 15px; color: black;'>", unsafe_allow_html=True)
    st.subheader("📝 Publicar nuevo aviso")
    
    with st.form("form_nuevo"):
        origen = st.text_input("Origen / Ciudad")
        detalle = st.text_input("Detalle (Ej: Maíz / Camión Térmico)")
        pago = st.text_input("Pago ofrecido / Tarifa")
        tel = st.text_input("WhatsApp (Solo números)")
        
        enviar = st.form_submit_button("🚀 PUBLICAR EN LA APP")
        
        if enviar:
            if origen and tel:
                # Leemos los datos actuales para agregar la nueva fila
                df_actual = conn.read(spreadsheet=URL_EXCEL, ttl=0)
                nueva_data = pd.DataFrame([{"origen": origen, "item": detalle, "pago": pago, "tel": tel}])
                
                # Juntamos y subimos al Excel
                df_final = pd.concat([df_actual, nueva_data], ignore_index=True)
                conn.update(spreadsheet=URL_EXCEL, data=df_final)
                
                st.success("✅ ¡Publicado! Ya aparece en el buscador.")
                st.balloons()
            else:
                st.error("Completá los campos obligatorios.")
    st.markdown("</div>", unsafe_allow_html=True)
