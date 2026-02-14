import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuración de Estilo e Interfaz (Manteniendo tu diseño)
st.set_page_config(page_title="Retorno Match", layout="wide")

# CSS para mantener el look oscuro y la imagen de fondo si la tenías
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión a la base de datos
conn = st.connection("gsheets", type=GSheetsConnection)

# Título Principal
st.title("🚛 Sistema de Retorno Match")

# Selector de Perfil (Interfaz anterior)
col_ch, col_em = st.columns(2)
with col_ch:
    soy_chofer = st.button("🚀 SOY CHOFER")
with col_em:
    soy_empresa = st.button("🏢 SOY EMPRESA")

st.markdown("---")

# Columnas de trabajo
col1, col2 = st.columns([1, 1.2])

# --- COLUMNA IZQUIERDA: PUBLICAR ---
with col1:
    st.subheader("📢 Publicar Camión")
    
    with st.container(border=True):
        # Usamos los nombres de campos de tu imagen
        ubicacion = st.text_input("📍 Ubicación (Punto de Retiro)")
        destino = st.text_input("🏁 Destino (Punto de Entrega)")
        equipo = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider"])
        whatsapp = st.text_input("📱 WhatsApp (ej: 543406123456)")
        nombre_empresa = st.text_input("🏢 Nombre de Empresa")
        
        if st.button("PUBLICAR"):
            if ubicacion and destino and whatsapp:
                try:
                    # Leer datos existentes para anexar
                    # IMPORTANTE: Usamos la pestaña "Respuestas de formulario 5" que se ve en tu imagen
                    df_actual = conn.read(worksheet="Respuestas de formulario 5")
                    
                    nueva_fila = pd.DataFrame([{
                        "Marca temporal": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Punto de Retiro": ubicacion,
                        "Punto de Entrega": destino,
                        "Mercadería": equipo,
                        "WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )": whatsapp,
                        "empresa": nombre_empresa,
                        "¿Cuándo carga?": "Inmediato"
                    }])
                    
                    df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Respuestas de formulario 5", data=df_final)
                    
                    st.success("✅ ¡Publicado con éxito!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Completa los campos obligatorios")

# --- COLUMNA DERECHA: VISUALIZACIÓN ---
with col2:
    st.subheader("📦 Cargas Disponibles")
    
    try:
        # Intentamos leer la pestaña de cargas
        df_visualizacion = conn.read(worksheet="Respuestas de formulario 5")
        
        if not df_visualizacion.empty:
            # Mostrar de más reciente a más antiguo
            for i, row in df_visualizacion.iloc[::-1].iterrows():
                # Solo mostrar si tiene punto de retiro
                if pd.notna(row['Punto de Retiro']):
                    with st.expander(f"📍 {row['Punto de Retiro']} ⮕ {row['Punto de Entrega']}"):
                        st.write(f"**🚛 Equipo:** {row['Mercadería']}")
                        st.write(f"**🏢 Empresa:** {row.get('empresa', 'N/A')}")
                        
                        # Limpieza de número de teléfono para el link
                        tel_clean = str(row['WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )']).replace(" ", "").replace("+", "")
                        st.markdown(f"[💬 Enviar WhatsApp](https://wa.me/{tel_clean})")
        else:
            st.info("No hay cargas publicadas.")
            
    except Exception as e:
        # Este es el error que te aparecía en rojo en la captura
        st.error("Error al conectar con Google Sheets. Verifica los permisos del archivo.")
