import streamlit as st
import urllib.parse

# 1. ESTILOS Y FONDO PROFESIONAL
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
    st.session_state.cargas = []
if 'camiones' not in st.session_state:
    st.session_state.camiones = []

# 3. CABECERA
st.markdown("<h1 style='text-align: center; color: white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ffcc00;'>Logística San Jorge, SF</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🛣️ BUSCAR CARGA", "📦 PUBLICAR CARGA", "🚛 PUBLICAR MI CAMIÓN"])

# --- TAB 1: EL CHOFER BUSCA CARGA ---
with tab1:
    filtro_origen = st.selectbox("¿Desde dónde buscás carga?", ["Todos", "Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
    
    cargas_filtradas = [c for c in st.session_state.cargas if filtro_origen == "Todos" or c['origen'] == filtro_origen]
    
    if not cargas_filtradas:
        st.info("No hay cargas disponibles para esa zona.")
    
    for c in cargas_filtradas:
        st.markdown(f"<div class='card-blanca'><strong>📍 {c['origen']} → San Jorge</strong><br><span>📦 Mercadería: {c['item']}</span><br><strong style='color: #2E7D32 !important;'>PAGO: ${c['pago']}</strong></div>", unsafe_allow_html=True)
        
        # MENSAJE PRO PARA EL DUEÑO DE LA CARGA
        texto_wa = f"🚛 *RETORNO MATCH*\n\n¡Hola! Vi tu publicación:\n📍 *Origen:* {c['origen']}\n📦 *Carga:* {c['item']}\n💰 *Pago:* ${c['pago']}\n\n¿Sigue disponible para cargar?"
        link_wa = f"https://wa.me/54{c['tel']}?text={urllib.parse.quote(texto_wa)}"
        
        st.markdown(f'<a href="{link_wa}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:25px;text-align:center;font-weight:bold;margin-bottom:20px;box-shadow: 0px 4px 8px rgba(0,0,0,0.3);">📲 CONTACTAR AL DUEÑO</div></a>', unsafe_allow_html=True)

# --- TAB 2: EL CLIENTE PUBLICA CARGA ---
with tab2:
    with st.form("form_c"):
        st.write("### Datos de la mercadería")
        p = st.text_input("¿Qué mercadería es?")
        t_dueño = st.text_input("Tu WhatsApp (Ej: 3406411222)")
        o = st.selectbox("Origen", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires", "Rafaela"])
        pa = st.number_input("Pago ofrecido ($)", min_value=1000, step=1000)
        if st.form_submit_button("🚀 PUBLICAR"):
            if p and t_dueño:
                st.session_state.cargas.append({"origen": o, "item": p, "pago": pa, "tel": t_dueño.replace(" ", "").replace("-", "")})
                st.success("¡Carga publicada! Ya la pueden ver los choferes.")
            else:
                st.error("Por favor completá mercadería y teléfono.")

# --- TAB 3: EL CHOFER PUBLICA CAMIÓN ---
with tab3:
    with st.form("form_cam"):
