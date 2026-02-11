import streamlit as st
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS PROFESIONALES
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
    
    label, p { color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS EN MEMORIA
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "item": "Repuestos Maquinaria", "pago": 55000},
        {"id": 2, "origen": "Santa Fe", "item": "Materiales Construcción", "pago": 42000}
    ]

# 3. CABECERA
st.markdown("<div class='titulo'>🚛 RETORNO MATCH</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitulo'>Logística Inteligente - San Jorge, SF</div>", unsafe_allow_html=True)

# 4. PESTAÑAS DE NAVEGACIÓN
tab1, tab2 = st.tabs(["🛣️ VISTA CHOFER", "📦 PUBLICAR CARGA"])

# --- VISTA PARA EL CAMIONERO ---
with tab1:
    st.write("### Cargas para tu regreso a San Jorge:")
    
    for c in st.session_state.cargas:
        with st.container():
            st.markdown(f"""
            <div class='card-carga'>
                <span style='color: #666; font-size: 12px;'>ID: #{c['id']}</span><br>
                <strong style='font-size: 20px; color: #1e3a8a;'>📍 {c['origen']} → San Jorge</strong><br>
                <p style='color: #333 !important; margin: 5px 0;'>📦 Carga: {c['item']}</p>
                <strong style='color: #2E7D32; font-size: 18px;'>PAGO OFRECIDO: ${c['pago']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Lógica de WhatsApp directo
            msg_texto = f"🚛 *RETORNO MATCH*\n¡Hola! Me interesa la carga de *{c['item']}* desde *{c['origen']}* hacia San Jorge. ¿Sigue disponible?"
            link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(msg_texto)}"
            
            if st.button(f"✅ CONTACTAR POR LA CARGA #{c
