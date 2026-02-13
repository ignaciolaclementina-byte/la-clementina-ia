import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. ESTILO
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-attachment: fixed;
    }
    .camion-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 12px 25px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. BOTÓN DE PUBLICAR
col1, col2, col3 = st.columns([1,1,1])
with col2:
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSc-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

st.write("---")

# 4. CARGA DE DATOS
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%202"

try:
    # Leemos el Excel
    df = pd.read_csv(URL)
    
    # --- LIMPIEZA INTELIGENTE ---
    # En tu foto image_77c944.png se ve que los datos reales están al fondo.
    # Vamos a buscar las columnas que tengan "Ubicación" y "Destino" sin importar donde estén.
    
    col_origen = [c for c in df.columns if 'Ubicación' in c or 'origen' in c.lower()]
    col_destino = [c for c in df.columns if 'Destino' in c or 'destino' in c.lower()]
    col_equipo = [c for c in df.columns if 'Equipo' in c or 'tipo de equipo' in c.lower()]
    col_tel = [c for c in df.columns if 'whatsapp' in c.lower()]

    # Si encontramos las columnas, armamos un resumen limpio
    if col_origen and col_destino:
        df_listado = pd.DataFrame({
            'fecha': df.iloc[:, 0], # La primera siempre es la fecha
            'origen': df[col_origen[0]],
            'destino': df[col_destino[0]],
            'equipo': df[col_equipo[0]] if col_equipo else "No especificado",
            'tel': df[col_tel[0]] if col_tel else "Sin Teléfono"
        })
        
        # Filtramos filas vacías
        df_listado = df_listado.dropna(subset=['origen', 'destino'])
        
        search = st.text_input("", placeholder="🔍 Buscar ciudad (Ej: Rosario, Córdoba...)")

        if not df_listado.empty:
            if search:
                df_listado = df_listado[df_listado['destino'].str.contains(search, case=False, na=False) | 
                                      df_listado['origen'].str.contains(search, case=False, na=False)]

            for _, row in df_listado.iloc[::-1].iterrows():
                # Limpiamos el teléfono
                t = str(row['tel']).split('.')[0].replace(" ", "").replace("+", "")
                tel_final = "".join(filter(str.isdigit, t))
                
                texto_wa = "Hola! Vi tu camion de " + str(row['origen']) + " a " + str(row['destino']) + " en Retorno Match."
                link_wa = "https://wa.me/" + tel_final + "?text=" + urllib.parse.quote(texto_wa)
                
                st.markdown(f"""
                <div class="camion-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="color: black; margin:0;">📍 {str(row['origen']).upper()} ⮕ {str(row['destino']).upper()}</h3>
                            <p style="color: #444; margin: 5px 0;"><b>🚛 Equipo:</b> {row['equipo']}</p>
                            <small style="color: #888;">Publicado: {row['fecha']}</small>
                        </div>
                        <a href="{link_wa}" target="_blank" class="btn-wa">📱 WHATSAPP</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p style='text-align:center; color:white;'>No hay viajes cargados aún.</p>", unsafe_allow_html=True)
    else:
        st.info("Sincronizando columnas del formulario...")

except Exception as e:
    st.error("Conectando con la base de datos...")

st.markdown("<br><p style='text-align:center; color:white; opacity:0.6; font-size:12px;'>San Jorge 2026</p>", unsafe_allow_html=True)
