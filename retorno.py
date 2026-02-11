import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN Y ESTILO VISUAL
st.set_page_config(page_title="Retorno Match - La Clementina", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2ecc71;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
        margin-bottom: 15px;
    }
    .card-blanca * { color: #2c3e50 !important; }
    label, p, h3 { color: white !important; font-weight: bold; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #2ecc71; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS TEMPORAL
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA CON LOGO Y MÉTRICAS
st.markdown("<h1 style='text-align: center; color: white;'>🍎 LA CLEMENTINA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #2ecc71; margin-top: -20px;'>Retorno Match San Jorge</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Disponibles", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones Volviendo", len(st.session_state.camiones))

st.write("---")

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR CARGA", "🚛 PUBLICAR CAMIÓN"])

# --- TAB 1: BUSCAR CARGA (VISTA CHOFER) ---
with tab1:
    filtro = st.selectbox("Filtrar por ciudad de origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    encontrado = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            encontrado = True
            st.markdown(f"""
                <div class='card-blanca'>
                    <strong>📍 {c['origen']} → San Jorge</strong><br>
                    <span>📦 Mercadería: {c['item']}</span><br>
                    <strong style='color: #27ae60 !important;'>PAGO: ${c['pago']}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            # Formateo de mensaje profesional
            msg = f"🍎 *LA CLEMENTINA - RETORNO MATCH*\n\n¡Hola! Vi tu carga de *{c['item']}* en *{c['origen']}*.\n¿Sigue disponible para cargar?"
            link = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:30px;text-align:center;font-weight:bold;margin-bottom:25px;">📲 CONTACTAR AL DUEÑO</div></a>', unsafe_allow_html=True)
    
    if not encontrado:
        st.info("No hay cargas publicadas en esta zona actualmente.")

# --- TAB 2: PUBLICAR CARGA (VISTA CLIENTE) ---
with tab2:
    with st.form("nueva_carga", clear_on_submit=True):
        st.write("### Datos de la Carga")
        p = st.text_input("¿Qué necesita transportar?")
        t = st.text_input("Su WhatsApp (Ej: 3406123456)")
        o = st.selectbox("Desde dónde sale:", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela
