import streamlit as st
import urllib.parse

# 1. ESTILOS Y CONFIGURACIÓN
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
st.markdown("<p style='text-align: center; color: #ffcc00;'>Logística Inteligente - San Jorge</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛣️ VER CARGAS", "📦 PUBLICAR CARGA", "🚛 PUBLICAR MI CAMIÓN"])

# --- TAB 1: VISTA PARA EL CHOFER (BUSCAR CARGA) ---
with tab1:
    st.write("### Cargas disponibles para traer a San Jorge:")
    for c in st.session_state.cargas:
        st.markdown(f"""
        <div class='card-blanca'>
            <strong>📍 DESDE: {c['origen']} → San Jorge</strong><br>
            <span>📦 PRODUCTO: {c['item']}</span><br>
            <strong style='color: #2E7D32 !important; font-size: 18px;'>PAGO: ${c['pago']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        msg_carga = f"Hola! Me interesa la carga de {c['item']} desde {c['origen']} para San Jorge."
        link_carga = f"https://wa.me/543406649346?text={urllib.parse.quote(msg_carga)}"
        
        st.markdown(f'<a href="{link_carga}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 CONTACTAR POR ESTA CARGA</div></a>', unsafe_allow_html=True)

# --- TAB 2: VISTA PARA EL CLIENTE (PUBLICAR MERCADERÍA) ---
with tab2:
    st.write("### Publicar pedido de transporte")
    with st.form("form_carga"):
        prod = st.text_input("¿Qué necesitás traer?")
        orig = st.selectbox("Desde dónde", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pago = st.number_input("Pago ofrecido ($)", min_value=1000, step=1000)
        if st.form_submit_button("🚀 PUBLICAR PEDIDO"):
            st.session_state.cargas.append({"id": len(st.session_state.cargas)+1, "origen": orig, "item": prod, "pago": pago})
            st.success("¡Pedido publicado!")

# --- TAB 3: VISTA PARA EL CHOFER (PUBLICAR CAMIÓN VACÍO) ---
with tab3:
    st.write("### Avisá que volvés vacío para que te llamen")
    with st.form("form_camion"):
        nombre = st.text_input("Tu Nombre / Empresa")
        desde_vuelto = st.selectbox("¿De dónde volvés?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        tipo = st.selectbox("Tipo de camión", ["Chasis solo", "Acoplado", "Sider", "Térmico"])
        if st.form_submit_button("📢 PUBLICAR MI VUELTA"):
            st.session_state.camiones.append({"nombre": nombre, "origen": desde_vuelto, "tipo": tipo})
            st.success("¡Camión publicado! Ahora figurás en la lista de disponibles.")

    if st.session_state.camiones:
        st.write("---")
        st.write("### Camiones volviendo ahora a San Jorge:")
        for cam in st.session_state.camiones:
            st.markdown(f"""
            <div class='card-blanca'>
                <strong>🚛 {cam['nombre']}</strong><br>
                <span>📍 Viene desde: {cam['origen']}</span><br>
                <span>⚙️ Tipo: {cam['tipo']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            msg_camion = f"Hola {cam['nombre']}! Vi que volvés de {cam['origen']} con un {cam['tipo']}. Tengo una carga para traerte."
            link_camion = f"https://wa.me/543406649346?text={urllib.parse.quote(msg_camion)}"
            
            st.markdown(f'<a href="{link_camion}" target="_blank" style="text-decoration:none;"><div style="background-color:#1e3a8a;color:white;padding:10px;border-radius:20px;text-align:center;font-weight:bold;margin-bottom:20px;">📲 LLAMAR AL CAMIONERO</div></a>', unsafe_allow_html=True)
