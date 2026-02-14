import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Retorno Match - Gestión de Cargas", layout="wide")

# 1. Conexión con Google Sheets
# Asegúrate de tener configurado .streamlit/secrets.toml con tus credenciales
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🚛 Sistema de Retorno Match")

# Creamos dos columnas para separar la publicación de la visualización
col1, col2 = st.columns([1, 1.5])

# --- COLUMNA 1: FORMULARIO DE PUBLICACIÓN ---
with col1:
    st.header("📢 Publicar Camión")
    
    with st.form("form_publicar_carga", clear_on_submit=True):
        ubicacion = st.text_input("📍 Ubicación (Punto de Retiro)")
        destino = st.text_input("🏁 Destino (Punto de Entrega)")
        equipo = st.selectbox("🚛 Equipo", ["Chasis", "Acoplado", "Semi", "Sider", "Térmico"])
        whatsapp = st.text_input("📱 WhatsApp (ej: 543406123456)")
        empresa = st.text_input("🏢 Nombre de Empresa")
        
        submitted = st.form_submit_button("PUBLICAR")

        if submitted:
            if ubicacion and destino and whatsapp:
                try:
                    # 1. Leer datos actuales para no sobrescribir
                    # Usamos la hoja "cargas" como se ve en tu estructura
                    existing_data = conn.read(worksheet="cargas")
                    
                    # 2. Crear nueva fila
                    new_data = pd.DataFrame([{
                        "Marca temporal": pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Punto de Retiro": ubicacion,
                        "Punto de Entrega": destino,
                        "Mercadería": equipo,
                        "WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )": whatsapp,
                        "empresa": empresa,
                        "¿Cuándo carga?": "Inmediato" # O puedes agregar un campo de fecha
                    }])
                    
                    # 3. Concatenar y actualizar
                    updated_df = pd.concat([existing_data, new_data], ignore_index=True)
                    conn.update(worksheet="cargas", data=updated_df)
                    
                    st.success("✅ ¡Carga publicada con éxito!")
                    st.rerun() 
                except Exception as e:
                    st.error(f"Error al guardar: {e}")
            else:
                st.warning("Por favor, completa los campos obligatorios.")

# --- COLUMNA 2: VISUALIZACIÓN DE CARGAS ---
with col2:
    st.header("📦 Cargas Disponibles")
    
    try:
        # Leer las cargas vigentes desde el Google Sheet
        df_cargas = conn.read(worksheet="cargas")
        
        if not df_cargas.empty:
            # Invertimos el DataFrame para ver las más recientes primero
            for index, row in df_cargas.iloc[::-1].iterrows():
                # Verificamos que la fila tenga datos antes de mostrarla
                if pd.notna(row['Punto de Retiro']):
                    with st.expander(f"📍 {row['Punto de Retiro']} ➡️ {row['Punto de Entrega']}"):
                        st.write(f"**🚛 Equipo:** {row['Mercadería']}")
                        st.write(f"**🏢 Empresa:** {row.get('empresa', 'No especificado')}")
                        
                        # Botón directo para WhatsApp
                        tel = str(row.get('WhatsApp Empresa ( sin 0 ni 15 ej: 54 3406 640000 )', '')).replace(" ", "")
                        st.markdown(f"[💬 Contactar por WhatsApp](https://wa.me/{tel})")
                        
                        st.caption(f"Publicado el: {row.get('Marca temporal', 'N/A')}")
        else:
            st.info("No hay cargas disponibles en este momento.")
            
    except Exception as e:
        st.error("Error al cargar los datos de la base de datos.")
