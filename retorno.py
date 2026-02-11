import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILOS
st.set_page_config(page_title="Retorno Match - San Jorge", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #ffcc00;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .card-blanca * { color: #333 !important; }
    label, p, h3 { color: white !important; font-weight: bold; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA Y CONTADORES
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Activas", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones en Viaje", len(st.session_state.camiones))

st.write("---")

tab1, tab2, tab3 = st.tabs(["🛣️ BUSCAR CARGA", "📦 PUBLICAR CARGA", "🚛 PUBLICAR MI CAMIÓN"])

# --- TAB 1: EL CHOFER BUSCA CARGA ---
with tab1:
    filtro = st.selectbox("¿Desde dónde buscás?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    encontrado = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            encontrado = True
            st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 {c['item']}</span><br><strong style='color: #2E7D32 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
            
            # Mensaje Pro para el cliente
            texto_wa = f"🚛 *RETORNO MATCH*\n\nHola! Vi tu carga de *{c['item']}* desde *{c['origen']}*.\n¿Sigue disponible para cargar?"
            link_wa = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:25px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    
    if not encontrado:
        st.info("No hay cargas para mostrar en esta zona
