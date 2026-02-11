import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
st.set_page_config(page_title="La Clementina - Retorno Match", layout="centered")

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

# 2. INICIALIZACIÓN DE DATOS (Evita errores de sesión vacía)
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA CON LOGO Y MÉTRICAS (Contadores solicitados)
st.markdown("<h1 style='text-align: center; color: white;'>🍎 LA CLEMENTINA</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #2ecc71; margin-top: -20px;'>Logística San Jorge</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("📦 Cargas Disponibles", len(st.session_state.cargas))
with col2:
    st.metric("🚛 Camiones en Viaje", len(st.session_state.camiones))

st.write("---")

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2, tab3 = st.tabs(["🔍 BUSCAR CARGA", "📤 PUBLICAR CARGA", "🚛 MI CAMIÓN"])

# --- TAB 1: BUSCAR CARGA (VISTA CHOFER) ---
with tab1:
    filtro = st.selectbox("Filtrar por origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    encontrado = False
    for c in st.session_state.cargas:
        if filtro == "Todos" or c['origen'] == filtro:
            encontrado = True
            st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 Mercadería: {c['item']}</span><br><strong style='color: #27ae60 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
            
            # Mensaje directo de WhatsApp con formato pro
            texto_wa = f"🍎 *LA CLEMENTINA*\n\n¡Hola! Vi tu carga de *{c['item']}* desde *{c['origen']}*.\n¿Sigue disponible?"
            link_wa = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(texto_wa)}"
            st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:30px;text-align:center;font-weight:bold;margin-bottom:25px;">📲 CONTACTAR AL DUEÑO</div></a>', unsafe_allow_html=True)
    
    if not encontrado:
        st.info("No hay cargas publicadas en esta zona por el momento.")

# --- TAB 2: PUBLICAR CARGA (VISTA CLIENTE) ---
with tab2:
    with st.form("form_c", clear_on_submit=True):
        st.write("### Datos de la Carga")
        p = st.text_input("¿Qué mercadería es?")
        t = st.text_input("Tu WhatsApp (Ej: 3406123456)")
        o = st.selectbox("Origen:", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pa = st.number_input("Pago ofrecido ($)", min_value=0, step=1000)
        
        if st.form_submit_button("🚀 PUBLICAR CARGA"):
            if p and t:
                st.session_state.cargas.append({"origen": o, "item": p, "pago": pa, "tel": t.replace(" ", "")})
                st.success("¡Carga publicada correctamente!")
                st.rerun()
            else:
                st.error("Por favor, completá mercadería y teléfono.")

# --- TAB 3: PUBLICAR CAMIÓN (VISTA CHOFER) ---
with tab3:
    with st.form("form_cam", clear_on_submit=True):
        st.write("### Datos del Camión")
        n = st.text_input("Nombre o Empresa")
        tel_c = st.text_input("WhatsApp (Ej: 3406123456)")
        d = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        tipo = st.selectbox("Unidad:", ["Chasis solo", "Acoplado", "Sider", "Térmico", "Batea"])
        
        if st.form_submit_button("📢 PUBLICAR MI VUELTA"):
            if n and tel_c:
                st.session_state.camiones.append({"nombre": n, "tel": tel_c.replace(" ", ""), "origen": d, "tipo": tipo})
                st.success("¡Camión en lista!")
                st.rerun()
            else:
                st.error("Completá nombre y teléfono.")

    st.write("---")
    st.write("### Camiones volviendo ahora:")
    for cam in st.session_state.camiones:
        st.markdown(f"<div class='card-blanca'><strong>🚛 {cam['nombre']}</strong><br><span>📍 Viene desde: {cam['origen']}</span><br><span>⚙️ Equipo: {cam['tipo']}</span></div>", unsafe_allow_html=True)
        
        msg_c = f"🍎 *LA CLEMENTINA*\n\nHola {
