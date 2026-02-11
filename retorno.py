import streamlit as st
import urllib.parse

# 1. ESTILOS Y FONDO (Mantenemos tu estética de montaña)
st.set_page_config(page_title="Retorno Match - San Jorge", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .card-carga {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #ffcc00;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
        margin-bottom: 10px;
    }
    .card-carga * { color: #333 !important; }
    label, p, h3 { color: white !important; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.1);
        border-radius: 10px 10px 0 0;
        color: white;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE DATOS (Evita el error NameError)
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos", "pago": 45000},
        {"id": 2, "origen": "Santa Fe", "item": "Cemento", "pago": 32000}
    ]

# 3. TÍTULO
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffcc00;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛣️ VISTA CHOFER", "📦 PUBLICAR CARGA"])

# --- PESTAÑA CHOFER ---
with tab1:
    st.write("### Cargas disponibles para tu regreso:")
    for c in st.session_state.cargas:
        # Mostramos la tarjeta blanca con la info
        st.markdown(f"""
        <div class='card-carga'>
            <strong style='font-size: 18px;'>📍 {c['origen']} → San Jorge</strong><br>
            <span>📦 Mercadería: {c['item']}</span><br>
            <strong style='color: #2E7D32 !important; font-size: 18px;'>PAGO: ${c['pago']}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        # MENSAJE DE WHATSAPP AUTOMÁTICO
        msg = f"🚛 *RETORNO MATCH*\n¡Hola! Me interesa la carga de *{c['item']}* desde *{c['origen']}* hacia San Jorge. ¿Sigue disponible?"
        link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(msg)}"
        
        # BOTÓN VERDE PERMANENTE
        st.markdown(f"""
            <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 25px; text-align: center; font-weight: bold; margin-bottom: 25px; box-shadow: 0px 4px 8px rgba(0,0,0,0.4);">
                    📲 CONTACTAR POR WHATSAPP
                </div>
            </a>
        """, unsafe_allow_html=True)

# --- PESTAÑA PUBLICAR ---
with tab2:
    st.write("### ¿Qué necesitás traer?")
    with st.form("form_carga"):
        prod = st.text_input("Mercadería (ej: Repuestos)")
        orig = st.selectbox("Desde dónde", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pago = st.number_input("Pago ofrecido ($)", min_value=1000, step=1000)
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            nuevo = {"id": len(st.session_state.cargas) + 1, "origen": orig, "item": prod, "pago": pago}
            st.session_state.cargas.append(nuevo)
            st.success("¡Publicado! Ya lo pueden ver los choferes.")
