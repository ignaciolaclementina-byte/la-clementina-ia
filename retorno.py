import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA Y DISEÑO
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2ecc71;
        margin-bottom: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    .card-blanca * { color: #2c3e50 !important; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #2ecc71; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS EN MEMORIA
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA Y CONTADORES (FOTO image_d174e1.jpg)
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important; font-size: 20px;'>🍎 La Clementina - Logística</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Disponibles", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones en Ruta", len(st.session_state.camiones))

st.write("---")

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR CARGA", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCADOR DE CARGAS ---
with tab1:
    filtro = st.selectbox("¿Desde dónde buscás carga?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    hay_cargas = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            hay_cargas = True
            st.markdown(f"""
                <div class='card-blanca'>
                    <strong>📍 {c['origen']} → San Jorge</strong><br>
                    <span>📦 Carga: {c['item']}</span><br>
                    <span style='color: #27ae60 !important;'>PAGO: ${c['pago']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón de WhatsApp corregido (Evita error de image_d16e78.jpg)
            msg_wa = f"🚛 *RETORNO MATCH*\n\nHola! Vi tu carga de *{c['item']}* en *{c['origen']}*.\n¿Sigue disponible?"
            link_wa = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(msg_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:30px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    
    if not hay_cargas:
        st.info("No hay cargas publicadas en esta zona por ahora.")

# --- TAB 2: PUBLICAR UNA CARGA ---
with tab2:
    with st.form("form_nueva_carga", clear_on_submit=True):
        st.write("### Datos para los Choferes")
        i_c = st.text_input("¿Qué hay que cargar?")
        t_c = st.text_input("Tu WhatsApp (Ej: 3406123456)")
        o_c = st.selectbox("Sale desde:", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        p_c = st.number_input("Pago ofrecido ($)", min_value=0, step=1000)
        
        if st.form_submit_button("🚀 PUBLICAR"):
            if i_c and t_c:
                st.session_state.cargas.append({"origen": o
