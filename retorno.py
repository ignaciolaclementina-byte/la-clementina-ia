import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA E INTERFAZ ANTERIOR
st.set_page_config(page_title="Retorno Match", layout="wide")

# Mantenemos tu estilo personalizado (Fondo oscuro y botones)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url("https://images.unsplash.com/photo-1519003722824-194d4455a60c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1740&q=80");
        background-size: cover;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #444;
    }
    .main-title {
        color: white;
        font-size: 40px;
        font-weight: bold;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN A BASE DE DATOS
conn = st.connection("gsheets", type=GSheetsConnection)

# Título con el emoji de camión de tu interfaz
st.markdown('<p class="main-title">🚚 Sistema de Retorno Match</p>', unsafe_allow_html=True)

# Selector de Perfil (SOY CHOFER / SOY EMPRESA)
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    st.button("🚀 SOY CHOFER")
with col_btn2:
    st.button("🏢 SOY EMPRESA")

st.markdown("---")

# 3. ESTRUCTURA DE DOS COLUMNAS
col_form, col_view = st.columns([1, 1.2])

# --- COLUMNA IZQUIERDA: PUBLICAR CAMIÓN ---
with col_form:
    st.subheader("📢 Publicar Camión")
    
    with st.container(border=True):
        # Campos con los nombres exactos de tu UI
        ubicacion = st.text_input("📍 Ubicación (Punto de Retiro)")
        destino = st.text_input("🏁 Destino (Punto de Entrega)")
        equipo = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
        whatsapp = st.text_input("📱 WhatsApp (ej: 543406123456)")
        nombre_empresa = st.text_input("🏢 Nombre de Empresa")
        
        if st.button("PUBLICAR"):
            if ubicacion and destino and whatsapp:
                try:
                    # LEER: Usamos el nombre de pestaña que se ve en tu imagen
                    df_original = conn.read(worksheet="Respuestas de formulario 5")
                    
                    # NUEVA FILA: Respetando el orden de tus columnas de Google Sheets
                    nueva_carga = pd.DataFrame([{
                        "Marca temporal": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Punto de Retiro": ubicacion,
                        "Punto de Entrega": destino,
                        "Mercadería": equipo,
                        "WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )": whatsapp,
                        "empresa": nombre_empresa,
                        "¿Cuándo carga?": "Inmediato"
                    }])
                    
                    # ACTUALIZAR
                    df_actualizado = pd.concat([df_original, nueva_carga], ignore_index=True)
                    conn.update(worksheet="Respuestas de formulario 5", data=df_actualizado)
                    
                    st.success("✅ Carga publicada en el sistema")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
            else:
                st.warning("⚠️ Por favor completa los campos con emoji de ubicación, destino y WhatsApp")

# --- COLUMNA DERECHA: CARGAS DISPONIBLES ---
with col_view:
    st.subheader("📦 Cargas Disponibles")
    
    try:
        # Leemos la misma pestaña para visualizar
        df_cargas = conn.read(worksheet="Respuestas de formulario 5")
        
        if not df_cargas.empty:
            # Mostramos las últimas cargas arriba (invertido)
            for i, row in df_cargas.iloc[::-1].iterrows():
                # Verificamos que la fila no esté vacía
                if pd.notna(row['Punto de Retiro']) and row['Punto de Retiro'] != "":
                    with st.expander(f"📍 {row['Punto de Retiro']} ⮕ {row['Punto de Entrega']}"):
                        st.write(f"**🚛 Equipo:** {row['Mercadería']}")
                        st.write(f"**🏢 Empresa:** {row.get('empresa', 'Particular')}")
                        
                        # Link de WhatsApp limpio
                        num_tel = str(row['WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )']).replace(" ", "").replace("+", "")
                        st.markdown(f"[💬 Contactar por WhatsApp](https://wa.me/{num_tel})")
                        
                        st.caption(f"Publicado: {row.get('Marca temporal', 'Reciente')}")
        else:
            st.info("No hay cargas publicadas actualmente.")
            
    except Exception as e:
        # Este bloque soluciona el mensaje rojo de tus capturas
        st.error("🔄 Sincronizando con Google Sheets... Verifica los permisos de 'Editor' para la cuenta de servicio.")
