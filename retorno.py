import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
st.set_page_config(page_title="Retorno Match - San Jorge", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop");
        background-size: cover !important;
    }
    .titulo { color: #f8f9fa; text-align: center; font-size: 35px; font-weight: bold; text-shadow: 2px 2px 4px #000; margin-bottom: 0px; }
    .subtitulo { color: #ffcc00; text-align: center; font-size: 18px; font-weight: bold; margin-bottom: 20px; }
    
    .card-carga {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        color: #333;
        border-left: 10px solid #ffcc00;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 15px;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 25px;
        background-color: #1e3a8a !important;
        color: white !important;
        font-weight: bold;
    }
    
    label, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS EN MEMORIA
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos Maquinaria", "pago": 55000},
        {"id": 2, "origen": "Santa Fe", "item": "Materiales Construcción", "pago": 42000},
        {"id": 3, "origen": "Córdoba", "item": "Insumos Agro", "pago": 85000}
    ]

# 3. CABECERA
st.markdown("<div class='titulo'>🚛 RETORNO MATCH</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Logística Inteligente - San Jorge, SF</div>", unsafe_allow_html=True)

# 4. PESTAÑAS
tab1, tab2 = st.tabs(["🛣️ VISTA CHOFER", "📦 PUBLICAR CARGA"])

# --- VISTA PARA EL CAMIONERO ---
with tab1:
    st.write("### Cargas para tu regreso a San Jorge:")
    
    for c in st.session_state.cargas:
        with st.container():
            st.markdown(f"""
            <div class='card-carga'>
                <span style='color: #666; font-size: 12px;'>ID: #{c['id']}</span><br>
                <strong style='font-size: 20px;'>📍 {c['origen']} → San Jorge</strong><br>
                <p style='color: #333 !important; margin: 5px 0;'>📦 Carga: {c['item']}</p>
                <strong style='color: #1e3a8a; font-size: 18px;'>PAGO: ${c['pago']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Lógica de WhatsApp
            mensaje = f"🚛 *RETORNO MATCH*\n¡Hola! Me interesa la carga de *{c['item']}* desde *{c['origen']}* hacia San Jorge. ¿Sigue disponible?"
            link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(mensaje)}"
            
            if st.button(f"✅ TOMAR CARGA #{c['id']}", key=f"btn_{c['id']}"):
                st.markdown(f"""
                    <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #25D366; color: white; padding: 15px; border-radius: 30px; text-align: center; font-weight: bold; margin-top: -10px; margin-bottom: 20px;">
                            📲 ENVIAR WHATSAPP AL CLIENTE
                        </div>
                    </a>
                """, unsafe_allow_html=True)

# --- VISTA PARA EL CLIENTE (COMERCIOS) ---
with tab2:
    st.write("### ¿Qué necesitás traer a San Jorge?")
    with st.form("form_nueva_carga"):
        producto = st.text_input("Mercadería (ej. Pallets de Cemento)")
        origen_merc = st.selectbox("Origen", ["Rosario", "Santa Fe",
