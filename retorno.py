import streamlit as st
import pandas as pd
import urllib.parse

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# 2. ESTILO ORIGINAL (Bordes verdes y tarjetas blancas)
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
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 10px solid #25D366; /* El borde verde que te gustaba */
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .btn-wa {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        float: right;
    }
    .city-text {
        color: #1a1a1a;
        font-size: 22px;
        font-weight: bold;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white; font-size: 50px;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# 3. BOTÓN DE PUBLICAR
col1, col2, col3 = st.columns([1,1,1])
with col2:
    LINK_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScC-OLmU8VbJgv0BLkLZ-9CH4i27bkwKa3zbv-QiguLbNE9pQ/viewform"
    st.link_button("➕ PUBLICAR MI CAMIÓN", LINK_FORM, use_container_width=True)

st.write("---")

# 4. CARGA DE DATOS INTELIGENTE
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Respuestas%20de%20formulario%202"

try:
    df = pd.read_csv(URL)
    
    # Buscamos las columnas por nombre (como se ven en tu imagen image_77c944.png)
    # Si Google cambia los nombres, el código intenta adaptarse
    col_ori = [c for c in df.columns if 'Ubicación' in c or 'origen' in c.lower()][0]
    col_des = [c for c in df.columns if 'Destino' in c or 'destino' in c.lower()][0]
    col_equ = [c for c in df.columns if 'Equipo' in c or 'tipo' in c.lower()][0]
    col_tel = [c for c in df.columns if 'whatsapp' in c.lower() or 'WhatsApp' in c][0]

    # Filtramos para que solo muestre filas donde haya una ubicación cargada
    df_lista = df[df[col_ori].notna()].copy()

    search = st.text_input("", placeholder="🔍 Filtrar por destino (Ej: Rosario, Córdoba...)")

    if not df_lista.empty:
        if search:
            df_lista = df_lista[df_lista[col_des].str.contains(search, case=False, na=False) | 
                               df_lista[col_ori].str.contains(search, case=False, na=False)]

        # Mostrar tarjetas (de la más nueva a la más vieja)
        for _, row in df_lista.iloc[::-1].iterrows():
            # Limpiar el teléfono para el link
            t = "".join(filter(str.isdigit, str(row[col_tel])))
            
            # Mensaje de WhatsApp
            texto_wa = f"Hola! Vi tu retorno de {row[col_ori]} a {row[col_des]} en Retorno Match."
            link_wa = f"https://wa.me/{t}?text={urllib.parse.quote(texto_wa)}"
            
            st.markdown(f"""
            <div class="camion-card">
                <a href="{link_wa}" target="_blank" class="btn-wa">📱 CONTACTAR</a>
                <p class="city-text">📍 {str(row[col_ori]).upper()} ⮕ {str(row[col_des]).upper()}</p>
                <p style="color: #555; margin: 5px 0;"><b>Camión:</b> {row[col_equ]}</p>
                <small style="color: #999;">Publicado: {row.iloc[0]}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:white;'>No hay camiones disponibles en este momento.</h3>", unsafe_allow_html=True)

except Exception as e:
    st.info("Conectando con la base de datos de camiones...")

st.markdown("<br><p style='text-align:center; color:gray; font-size:12px;'>Logística San Jorge 2026</p>", unsafe_allow_html=True)
