import streamlit as st
import urllib.parse

# 1. ESTILO Y CONFIGURACIÓN
st.set_page_config(page_title="Retorno Match - San Jorge", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-size: cover !important;
    }
    .card-carga {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #ffcc00;
        margin-bottom: 15px;
    }
    .card-carga * { color: #333 !important; }
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background-color: #1e3a8a !important;
        color: white !important;
    }
    label, p, h3 { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATOS INICIALES
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos Maquinaria", "pago": 55000},
        {"id": 2, "origen": "Santa Fe", "item": "Materiales Construcción", "pago": 42000}
    ]

# 3. CABECERA
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffcc00 !important;'>San Jorge, Santa Fe</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🛣️ VISTA CHOFER", "📦 PUBLICAR CARGA"])

# --- VISTA CHOFER ---
with tab1:
    st.write("### Cargas disponibles:")
    for c in st.session_state.cargas:
        with st.container():
            st.markdown(f"""
            <div class='card-carga'>
                <strong>📍 {c['origen']} → San Jorge</strong><br>
                <span>📦 Carga: {c['item']}</span><br>
                <strong style='color: #2E7D32 !important;'>PAGO: ${c['pago']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # WhatsApp corregido sin errores de llaves
            msg = f"Hola! Me interesa la carga {c['item']} desde {c['origen']} a San Jorge."
            link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(msg)}"
            
            if st.button(f"✅ CONTACTAR POR CARGA #{c['id']}", key=f"btn_{c['id']}"):
                st.markdown(f'<a href="{link_wa}" target="_blank"><div style="background-color: #25D366; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold;">📲 ABRIR WHATSAPP</div></a>', unsafe_allow_html=True)

# --- VISTA CLIENTE ---
with tab2:
    st.write("### Publicar mercadería")
    with st.form("form_carga"):
        prod = st.text_input("¿Qué mercadería es?")
        orig = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pago = st.number_input("Pago ofrecido ($)", min_value=1000, step=1000)
        
        if st.form_submit_button("🚀 PUBLICAR"):
            nuevo = {"id": len(st.session_state.cargas) + 1, "origen": orig, "item": prod, "pago": pago}
            st.session_state.cargas.append(nuevo)
            st.success("¡Publicado!")
