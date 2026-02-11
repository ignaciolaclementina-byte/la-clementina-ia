import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN Y DISEÑO DE LA APP
st.set_page_config(page_title="Retorno Match - San Jorge", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-size: cover !important;
        background-attachment: fixed !important;
    }
    .titulo { color: #f8f9fa; text-align: center; font-size: 35px; font-weight: bold; text-shadow: 2px 2px 4px #000; margin-bottom: 0px; }
    .subtitulo { color: #ffcc00; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px; }
    
    .card-carga {
        background-color: white !important;
        padding: 20px;
        border-radius: 15px;
        color: #333 !important;
        border-left: 10px solid #ffcc00;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
        margin-bottom: 15px;
    }
    .card-carga * { color: #333 !important; }
    
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background-color: #1e3a8a !important;
        color: white !important;
        font-weight: bold;
        height: 45px;
    }
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS TEMPORAL
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos Maquinaria", "pago": 55000},
        {"id": 2, "origen": "Santa Fe", "item": "Materiales Construcción", "pago": 42000}
    ]

# 3. CABECERA
st.markdown("<div class='titulo'>🚛 RETORNO MATCH</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Logística Inteligente - San Jorge, SF</div>", unsafe_allow_html=True)

# 4. PESTAÑAS
tab1, tab2 = st.tabs(["🛣️ VISTA CHOFER", "📦 PUBLICAR CARGA"])

# --- VISTA PARA EL CAMIONERO ---
with tab1:
    st.write("### Cargas disponibles para volver:")
    for c in st.session_state.cargas:
        with st.container():
            st.markdown(f"""
            <div class='card-carga'>
                <small>ID: #{c['id']}</small><br>
                <strong style='font-size: 20px;'>📍 {c['origen']} → San Jorge</strong><br>
                <span>📦 Carga: {c['item']}</span><br>
                <strong style='color: #2E7D32 !important; font-size: 18px;'>PAGO: ${c['pago']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Link de WhatsApp corregido
            msg = f"🚛 *RETORNO MATCH*\nMe interesa la carga de *{c['item']}* desde *{c['origen']}* hacia San Jorge. ¿Sigue disponible?"
            link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(msg)}"
            
            if st.button(f"✅ TOMAR CARGA #{c['id']}", key=f"btn_{c['id']}"):
                st.markdown(f"""
                    <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; margin-top: -10px; margin-bottom: 20px;">
                            📲 ABRIR WHATSAPP AHORA
                        </div>
                    </a>
                """, unsafe_allow_html=True)

# --- VISTA PARA EL CLIENTE ---
with tab2:
    st.write("### Publicá tu mercadería")
    with st.form("nueva_carga"):
        prod = st.text_input("Mercadería (ej. 2 Pallets de Cemento)")
        orig = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "
