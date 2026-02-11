import streamlit as st

# CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Retorno Match", layout="centered")

# Inicializamos la lista de cargas en la memoria de la app
if 'cargas' not in st.session_state:
    st.session_state.cargas = [
        {"id": 1, "origen": "Rosario", "destino": "San Jorge", "item": "Repuestos", "pago": 45000},
        {"id": 2, "origen": "Santa Fe", "destino": "San Jorge", "item": "Cemento", "pago": 32000}
    ]

# TÍTULO
st.title("🚛 Retorno Match")
st.write("Conectando camiones vacíos con carga para San Jorge.")

# FORMULARIO PARA EL CLIENTE (El que necesita traer algo)
st.header("📦 Publicar Pedido")
with st.form("nuevo_pedido"):
    producto = st.text_input("¿Qué mercadería es?")
    desde = st.selectbox("¿Desde dónde?", ["Rosario", "Santa Fe", "Córdoba", "Buenos Aires"])
    oferta = st.number_input("¿Cuánto ofrecés pagar?", min_value=1000, step=500)
    
    boton_publicar = st.form_submit_button("Publicar Pedido")

    if boton_publicar:
        nuevo = {
            "id": len(st.session_state.cargas) + 1,
            "origen": desde,
            "destino": "San Jorge",
            "item": producto,
            "pago": oferta
        }
        st.session_state.cargas.append(nuevo)
        st.success("¡Pedido publicado!")

# VISTA PARA EL CAMIONERO (El que busca carga)
st.divider()
st.header("🛣️ Cargas Disponibles")

for c in st.session_state.cargas:
    with st.expander(f"📍 {c['origen']} -> San Jorge | {c['item']}"):
        st.write(f"**Pago:** ${c['pago']}")
        if st.button(f"Tomar Carga #{c['id']}"):
            st.info("Conectando con el cliente...")
