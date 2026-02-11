import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .card-blanca {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #2ecc71;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
    }
    .card-blanca * { color: #2c3e50 !important; }
    .stMetric { background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 15px; border: 1px solid #2ecc71; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS TEMPORAL
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA Y CONTADORES (image_d174e1.jpg)
st.markdown("<h1 style='text-align: center;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #2ecc71 !important; font-size: 20px;'>🍎 La Clementina - Logística</p>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Disponibles", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones en Ruta", len(st.session_state.camiones))

st.write("---")

tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR", "📤 PUBLICAR CARGA", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCADOR ---
with tab1:
    filtro = st.selectbox("Filtrar por origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    encontrado = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            encontrado = True
            st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 Mercadería: {c['item']}</span><br><strong style='color: #27ae60 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
            
            # WhatsApp Dueño (Cerrando llaves correctamente para evitar error image_d16e78.jpg)
            msg_wa = f"🚛 *RETORNO MATCH*\n\nHola! Vi tu carga de *{c['item']}* en *{c['origen']}*.\n¿Sigue disponible?"
            link_wa = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(msg_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:30px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR DUEÑO</div></a>', unsafe_allow_html=True)
    
    if not encontrado:
        st.info("No hay cargas publicadas en esta zona actualmente.")

# --- TAB 2: PUBLICAR CARGA ---
with tab2:
    with st.form("form_c", clear_on_submit=True):
        st.write("### Datos de la Carga")
        i_c = st.text_input("¿Qué mercadería es?")
        t_c = st.text_input("WhatsApp (Ej: 3406123456)")
        o_c = st.selectbox("Origen:", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        p_c = st.number_input("Pago ofrecido ($)", min_value=0, step=1000)
        
        # Corrigiendo error de la línea 77 (image_d17598.jpg)
        if st.form_submit_button("🚀 PUBLICAR"):
            if i_c and t_c:
                st.session_state.cargas.append({"origen": o_c, "item": i_c, "pago": p_c, "tel": t_c.replace(" ", "")})
                st.success("¡Publicado!")
                st.rerun()
            else:
                st.error("Completá mercadería y teléfono.")

# --- TAB 3: PUBLICAR CAMIÓN ---
with tab3:
    with st.form("form_t", clear_on_submit=True):
        st.write("### Mi Camión")
        n_t = st.text_input("Nombre/Empresa")
        tl_t = st.text_input("WhatsApp (Ej: 3406123456)")
        og_t = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        tp_t = st.selectbox("Tipo:", ["Chasis solo", "Acoplado", "Sider", "Térmico"])
        
        if st.form_submit_button("📢 PUBLICAR VUELTA"):
            if n_t and tl_t:
                st.session_state.camiones.append({"nombre": n_t, "tel": tl_t.replace(" ", ""), "origen": og_t, "tipo": tp_t})
                st.success("¡En lista!")
                st.rerun()
            else:
                st.error("Faltan datos.")

    st.write("---")
    for cam in st.session_state.camiones:
        st.markdown(f"<div class='card-blanca'><strong>🚛 {cam['nombre']}</strong><br><span>📍 Origen: {cam['origen']}</span><br><span>⚙️ {cam['tipo']}</span></div>", unsafe_allow_html=True)
        msg_t = f"🍎 *LA CLEMENTINA*\n\nHola {cam['nombre']}! Vi que volvés de *{cam['origen']}*. Tengo una carga para vos."
        link_t = f"https://wa.me/54{cam['tel']}?text={urllib.parse.quote(msg_t)}"
        st.markdown(f'<a href="{link_t}" target="_blank" style="text-decoration:none;"><div style="background-color:#1e3a8a;color:white;padding:12px;border-radius:30px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 HABLAR CON CHOFER</div></a>', unsafe_allow_html=True)

# SIDEBAR ADMIN
with st.sidebar:
    st.write("## Administración")
    if st.button("🧹 Limpiar Pantalla"):
        st.session_state.cargas = []
        st.session_state.camiones = []
        st.rerun()
