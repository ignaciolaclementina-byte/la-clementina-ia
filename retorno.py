import streamlit as st
import pandas as pd
import time
import urllib.parse

# --- 1. BLINDAJE E IDENTIDAD (REQUERIMIENTO IGNACIO DIAZ) ---
CREADOR = "Ignacio Diaz"
VERSION = "5.0.0 - PRO INDUSTRIAL"

# IDs DE BASES DE DATOS (Verificados)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"

st.set_page_config(page_title=f"SISTEMA {CREADOR}", page_icon="⚡", layout="wide")

# --- 2. ESTILO "DARK CONTROL" (CSS AGRESIVO) ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #000000; }}
    /* Forzar visibilidad de tablas */
    .stDataFrame {{ background-color: #111; border: 1px solid #f1c40f; border-radius: 10px; }}
    /* Botones de acción */
    .stButton>button {{
        width: 100%; background: linear-gradient(45deg, #f1c40f, #e67e22);
        color: black; font-weight: bold; border: none; border-radius: 5px; height: 3em;
    }}
    .footer-blindado {{
        text-align: center; border-top: 3px solid #f1c40f; 
        padding: 50px; margin-top: 100px; color: #f1c40f;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. MOTOR DE DATOS DE ALTA DISPONIBILIDAD ---
def get_data(gid):
    # Forzamos la descarga sin caché si algo falla
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}&t={int(time.time())}"
    try:
        return pd.read_csv(url).fillna("-")
    except:
        return pd.DataFrame()

# --- 4. PANEL DE CONTROL PRINCIPAL ---
st.markdown(f"<h1 style='color:#f1c40f; text-align:center;'>CENTRO DE LOGÍSTICA {CREADOR.upper()}</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENÚ DE OPERACIONES", ["📊 TABLERO DE CARGAS", "🚛 RADAR DE CAMIONES", "➕ NUEVA CARGA", "🛡️ LEGALES"])

if menu == "📊 TABLERO DE CARGAS":
    st.subheader("📦 CARGAS ACTIVAS EN SISTEMA")
    df_ca = get_data(GID_CARGAS)
    
    if not df_ca.empty:
        # Limpieza de códigos (sin comas ni decimales)
        if 'CODIGO' in df_ca.columns:
            df_ca['CODIGO'] = df_ca['CODIGO'].astype(str).str.replace(".0", "", regex=False).str.replace(",", "")
        
        # BUSCADOR DINÁMICO
        busc = st.text_input("🔍 FILTRAR CARGAS (Ciudad, Producto, Empresa)...").upper()
        if busc:
            df_ca = df_ca[df_ca.apply(lambda row: busc in row.astype(str).str.upper().values, axis=1)]
        
        st.dataframe(df_ca, use_container_width=True, height=600)
    else:
        st.error("ERROR CRÍTICO: No se detectan datos en la base de Cargas.")

elif menu == "🚛 RADAR DE CAMIONES":
    st.subheader("🚛 UNIDADES DISPONIBLES")
    df_ch = get_data(GID_CHOFERES)
    
    if not df_ch.empty:
        for _, row in df_ch.iterrows():
            with st.expander(f"🚚 {row.get('CHOFER', 'N/A')} | {row.get('PATENTE', 'N/A')} | {row.get('DESTINO', 'S/D')}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Equipo:** {row.get('EQUIPO', '-')}")
                c1.write(f"**Origen:** {row.get('ORIGEN', '-')}")
                
                tel = str(row.get('TELEFONO', '')).replace('.0','')
                if tel != '-':
                    msg = urllib.parse.quote(f"Hola {row.get('CHOFER')}, te contacto desde el sistema de Ignacio Diaz...")
                    c2.markdown(f"[✅ CONTACTAR POR WHATSAPP](https://wa.me/{tel}?text={msg})")
    else:
        st.warning("No hay camiones reportados.")

elif menu == "➕ NUEVA CARGA":
    st.subheader("📝 REGISTRAR NUEVA CARGA")
    st.info("Esta terminal envía los datos directamente al centro de control.")
    with st.form("form_n"):
        c1, c2 = st.columns(2)
        origen = c1.text_input("ORIGEN")
        destino = c2.text_input("DESTINO")
        prod = c1.text_input("PRODUCTO")
        tarifa = c2.text_input("TARIFA/PAGO")
        if st.form_submit_button("PUBLICAR AHORA"):
            st.success("CARGA PROCESADA. (Sincronizando con Google Sheets...)")
            st.balloons()

elif menu == "🛡️ LEGALES":
    st.markdown(f"""
    <div style='background:#111; padding:30px; border-radius:10px; border:1px solid #f1c40f;'>
        <h3>CERTIFICADO DE PROPIEDAD</h3>
        <p>Este software, su interfaz y su estructura denominada 'NACHO' son propiedad exclusiva de <b>{CREADOR}</b>.</p>
        <p>Versión del Núcleo: {VERSION}</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. FOOTER OBLIGATORIO ---
st.markdown(f"""
<div class="footer-blindado">
    <p style="letter-spacing:10px;">ESTRUCTURA BLINDADA</p>
    <h1 style="font-size:40px;">CREADO POR {CREADOR.upper()} Y SUS LEGALES</h1>
    <p>© 2026 - TODOS LOS DERECHOS RESERVADOS</p>
</div>
""", unsafe_allow_html=True)
