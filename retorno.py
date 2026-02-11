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

# 2. INICIALIZACIÓN DE DATOS
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos", "pago": 45000},
        {"id": 2, "origen": "Santa Fe", "item": "Cemento", "pago": 32000}
    ]
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛣️ BUSCAR CARGA", "📦 PUBLICAR CARGA", "🚛 PUBLICAR MI CAMIÓN"])

# --- TAB 1: BUSCAR CARGA (VISTA CHOFER) ---
with tab1:
    filtro_origen = st.selectbox("¿Desde dónde buscás carga?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    for c in st.session_state.cargas:
        if filtro_origen == "Todos" or c['origen'] == filtro_origen:
            st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 Mercadería: {c['item']}</span><br><strong style='color: #2E7D32 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
            # Este mensaje sigue yendo a vos como administrador
            msg = f"Hola! Me interesa la carga de {c['item']} desde {c['origen']}."
            link = f"https://wa.me/543406649346?text={urllib.parse.quote(msg)}"
            st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR LOGÍSTICA</div></a>', unsafe_allow_html=True)

# --- TAB 2: PUBLICAR CARGA (CLIENTES) ---
with tab2:
    with st.form("f1"):
        p = st.text_input("¿Qué mercadería?")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pa = st.number_input("Pago ($)", min_value=1000)
        if st.form_submit_button("🚀 PUBLICAR"):
            st.session_state.cargas.append({"id": len(st.session_state.cargas)+1, "origen": o, "item": p, "pago": pa})
            st.success("¡Publicado!")

# --- TAB 3: PUBLICAR CAMIÓN (CON NÚMERO DE TELÉFONO) ---
with tab3:
    st.write("### Registrá tu camión vacío")
    with st.form("f2"):
        n = st.text_input("Tu Nombre")
        tel = st.text_input("Tu WhatsApp (Ej: 3406444555)", help="Sin el 0 y sin el 15")
        d = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        t = st.selectbox("Tipo de camión", ["Chasis solo", "Acoplado", "Sider", "Térmico"])
        if st.form_submit_button("📢 PUBLICAR MI VUELTA"):
            if n and tel:
                # Limpiamos el teléfono por si ponen espacios o guiones
                tel_clean = tel.replace(" ", "").replace("-", "")
                st.session_state.camiones.append({"nombre": n, "tel": tel_clean, "origen": d, "tipo": t})
                st.success("¡Tu camión ya figura en la lista!")
            else:
                st.error("Por favor completá tu nombre y teléfono.")

    st.write("---")
    st.write("### Camiones volviendo ahora:")
    filtro_cam = st.selectbox("Filtrar camiones por origen:", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"], key="fcam")
    
    for cam in st.session_state.camiones:
        if filtro_cam == "Todos" or cam['origen'] == filtro_cam:
            st.markdown(f"<div class='card-blanca'><strong>🚛 {cam['nombre']}</strong><br><span>📍 Viene desde: {cam['origen']}</span><br><span>⚙️ Tipo: {cam['tipo']}</span></div>", unsafe_allow_html=True)
            
            # EL BOTÓN AHORA USA EL NÚMERO DEL CAMIONERO
            msg_c = f"Hola {cam['nombre']}! Vi en Retorno Match que venís de {cam['origen']}. Tengo una carga para vos."
            link_c = f"https://wa.me/54{cam['tel']}?text={urllib.parse.quote(msg_c)}"
            
            st.markdown(f'<a href="{link_c}" target="_blank" style="text-decoration:none;"><div style="background-color:#1e3a8a;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 LLAMAR AL CAMIONERO DIRECTO</div></a>', unsafe_allow_html=True)
