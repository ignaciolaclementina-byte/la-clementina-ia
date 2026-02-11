import streamlit as st
import urllib.parse

# 1. ESTILOS Y FONDO
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
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS (Lista vacía para evitar errores de historial)
if 'cargas' not in st.session_state:
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛣️ BUSCAR CARGA", "📦 PUBLICAR CARGA", "🚛 PUBLICAR MI CAMIÓN"])

# --- TAB 1: BUSCAR CARGA (VISTA CHOFER) ---
with tab1:
    filtro_origen = st.selectbox("¿Desde dónde buscás carga?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    if not st.session_state.cargas:
        st.info("No hay cargas publicadas. ¡Sé el primero en publicar!")
    
    for c in st.session_state.cargas:
        if filtro_origen == "Todos" or c['origen'] == filtro_origen:
            st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 Mercadería: {c['item']}</span><br><strong style='color: #2E7D32 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
            
            # SEGURIDAD: Solo armar el link si existe 'tel'
            if 'tel' in c:
                msg_c = f"Hola! Vi tu carga de {c['item']} en Retorno Match. ¿Sigue disponible?"
                link_c = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(msg_c)}"
                st.markdown(f'<a href="{link_c}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR AL DUEÑO DIRECTO</div></a>', unsafe_allow_html=True)
            else:
                st.warning("Esta carga no tiene teléfono de contacto.")

# --- TAB 2: PUBLICAR CARGA (EL DUEÑO DEJA SU TEL) ---
with tab2:
    with st.form("f1"):
        p = st.text_input("¿Qué mercadería es?")
        t_dueño = st.text_input("Tu WhatsApp (Ej: 3406444555)")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pa = st.number_input("Pago ofrecido ($)", min_value=1000)
        if st.form_submit_button("🚀 PUBLICAR CARGA"):
            if p and t_dueño:
                st.session_state.cargas.append({"origen": o, "item": p, "pago": pa, "tel": t_dueño.replace(" ", "")})
                st.success("¡Publicado!")
            else:
                st.error("Completá mercadería y teléfono.")

# --- TAB 3: PUBLICAR CAMIÓN (EL CHOFER DEJA SU TEL) ---
with tab3:
    with st.form("f2"):
        n = st.text_input("Tu Nombre")
        tel_cam = st.text_input("Tu WhatsApp (Ej: 3406444555)")
        d = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        t = st.selectbox("Tipo de camión", ["Chasis solo", "Acoplado", "Sider", "Térmico"])
        if st.form_submit_button("📢 PUBLICAR MI VUELTA"):
            if n and tel_cam:
                st.session_state.camiones.append({"nombre": n, "tel": tel_cam.replace(" ", ""), "origen": d, "tipo": t})
                st.success("¡Camión publicado!")
    
    st.write("---")
    for cam in st.session_state.camiones:
        if 'tel' in cam:
            st.markdown(f"<div class='card-blanca'><strong>🚛 {cam['nombre']}</strong><br><span>📍 Origen: {cam['origen']}</span><br><span>⚙️ {cam['tipo']}</span></div>", unsafe_allow_html=True)
            msg_cam = f"Hola {cam['nombre']}! Tengo una carga desde {cam['origen']}."
            link_cam = f"https://wa.me/54{cam['tel']}?text={urllib.parse.quote(msg_cam)}"
            st.markdown(f'<a href="{link_cam}" target="_blank" style="text-decoration:none;"><div style="background-color:#1e3a8a;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 LLAMAR AL CAMIONERO DIRECTO</div></a>', unsafe_allow_html=True)

# BOTÓN DE ADMINISTRADOR PARA LIMPIAR (Solo para vos)
if st.sidebar.button("🧹 Limpiar base de datos"):
    st.session_state.cargas = []
    st.session_state.camiones = []
    st.sidebar.success("¡Datos borrados!")
