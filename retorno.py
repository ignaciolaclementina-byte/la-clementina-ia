import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN EXACTA (EXTRAÍDA DE TUS ENLACES) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"  # Pestaña 6 (Camiones)
GID_CARGAS = "1267917528"    # Pestaña 5 (Cargas)
ADMIN_PASSWORD = "1323" 

# URLS DE ENVÍO (Ya corregidas a formResponse)
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS (BOTONES GRANDES Y CLAROS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
                        url('https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    
    /* PESTAÑAS GIGANTES TIPO APP */
    .stTabs [data-baseweb="tab-list"] { display: flex; gap: 8px; width: 100%; }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; border: 2px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; border-color: white !important; }

    /* TARJETAS BLANCAS */
    .card-white {
        background: white !important; border-radius: 15px; padding: 15px; margin-bottom: 12px;
        border-left: 10px solid #3498db; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .route-txt { font-size: 20px; font-weight: 900; color: #1e3799; margin-bottom: 5px; }
    .info-tag { 
        background: #f1f2f6; padding: 5px 10px; border-radius: 6px; font-size: 14px; 
        color: #333; border: 1px solid #dfe6e9; display: inline-block; margin: 2px;
    }
    .btn-wsp { 
        background-color: #27ae60; color: white !important; padding: 10px 20px; 
        border-radius: 8px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 RETORNO MATCH")

# --- BOTÓN DE ACTUALIZACIÓN FORZADA ---
if st.button("🔄 ACTUALIZAR LISTADO"):
    st.cache_data.clear()
    st.rerun()

# --- BUSCADORES ---
c1, c2 = st.columns(2)
with c1: b_origen = st.text_input("📍 ORIGEN:").strip()
with c2: b_destino = st.text_input("🏁 DESTINO:").strip()

# PESTAÑAS PRINCIPALES
tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER (Busco Carga)", "🏢 SOY EMPRESA (Busco Camión)"])

# ==============================================================================
# PESTAÑA 1: SOY CHOFER (Aquí publican su camión y ven cargas de empresas)
# ==============================================================================
with tab_chofer:
    col_izq, col_der = st.columns([1, 2])
    
    # 1. FORMULARIO PARA CHOFERES (Suben a Hoja 6)
    with col_izq:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_chofer", clear_on_submit=True):
            ch_origen = st.text_input("📍 ¿Dónde estás?")
            ch_destino = st.text_input("🏁 ¿A dónde vas?")
            ch_equipo = st.selectbox("🚛 Tu Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Térmico"])
            ch_wsp = st.text_input("📱 Tu WhatsApp")
            
            if st.form_submit_button("PUBLICAR DISPONIBILIDAD"):
                # DATOS EXACTOS SEGÚN TUS ENLACES
                datos_ch = {
                    "entry.1304806144": ch_origen,
                    "entry.1519265625": ch_destino,
                    "entry.597193898": ch_equipo,
                    "entry.1574172378": ch_wsp
                }
                try:
                    requests.post(URL_CHOFERES_POST, data=datos_ch)
                    st.success("✅ ¡Publicado! Revisá la pestaña 'SOY EMPRESA'.")
                    time.sleep(2)
                    st.rerun()
                except:
                    st.error("Error de conexión.")

    # 2. VER CARGAS DE EMPRESAS (Leen de Hoja 5)
    with col_der:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            # Leemos Hoja 5 (Cargas)
            url_csv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}"
            df_cargas = pd.read_csv(url_csv).fillna("-")
            
            for _, row in df_cargas.iloc[::-1].iterrows():
                # MAPEO EXACTO HOJA 5:
                # Col B (1): Retiro | Col C (2): Entrega | Col D (3): Carga | Col E (4): WhatsApp | Col F (5): Empresa | Col G (6): Fecha
                ret, ent, car, tel, emp, fec = row[1], row[2], row[3], row[4], row[5], row[6]
                
                # Filtros
                if b_origen and b_origen.lower() not in str(ret).lower(): continue
                if b_destino and b_destino.lower() not in str(ent).lower(): continue
                
                msg = f"Hola! Vi tu carga de {ret} a {ent} ({car}) en Retorno Match. ¿Sigue disponible?"
                link = f"https://api.whatsapp.com/send?phone=549{tel}&text={urllib.parse.quote(msg)}"
                
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {str(ret).upper()} ➔ {str(ent).upper()}</div>
                    <div>
                        <span class="info-tag">🏢 {emp}</span>
                        <span class="info-tag">📦 {car}</span>
                        <span class="info-tag">⏳ {fec}</span>
                    </div>
                    <a href="{link}" target="_blank" class="btn-wsp">TOMAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.info("Esperando cargas...")

# ==============================================================================
# PESTAÑA 2: SOY EMPRESA (Aquí publican carga y ven camiones de choferes)
# ==============================================================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2])
    
    # 1. FORMULARIO PARA EMPRESAS (Suben a Hoja 5)
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("form_empresa", clear_on_submit=True):
            em_origen = st.text_input("📍 Retiro")
            em_destino = st.text_input("🏁 Entrega")
            em_carga = st.text_input("📦 Qué llevás")
            em_empresa = st.text_input("🏢 Nombre Empresa")
            em_fecha = st.selectbox("⏳ Cuándo", ["Sale hoy", "Sale mañana", "A convenir"])
            em_wsp = st.text_input("📱 WhatsApp")
            
            if st.form_submit_button("SUBIR CARGA"):
                # DATOS EXACTOS SEGÚN TUS ENLACES
                datos_em = {
                    "entry.610070407": em_origen,
                    "entry.170847116": em_destino,
                    "entry.576675281": em_carga,
                    "entry.1930562861": em_empresa,
                    "entry.1064058502": em_fecha,
                    "entry.466540450": em_wsp
                }
                try:
                    requests.post(URL_CARGAS_POST, data=datos_em)
                    st.success("✅ Carga subida correctamente.")
                    time.sleep(2)
                    st.rerun()
                except:
                    st.error("Error al subir.")

    # 2. VER CAMIONES DE CHOFERES (Leen de Hoja 6)
    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            # Leemos Hoja 6 (Choferes)
            url_csv_ch = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}"
            df_choferes = pd.read_csv(url_csv_ch).fillna("-")
            
            for _, row in df_choferes.iloc[::-1].iterrows():
                # MAPEO EXACTO HOJA 6:
                # Col B (1): Origen | Col C (2): Destino | Col D (3): Equipo | Col E (4): WhatsApp
                orig, dest, equi, telf = row[1], row[2], row[3], row[4]
                
                # Filtros
                if b_origen and b_origen.lower() not in str(orig).lower(): continue
                if b_destino and b_destino.lower() not in str(dest).lower(): continue
                
                msg_ch = f"Hola! Vi tu camión disponible en {orig} (Equipo: {equi}). Tengo una carga."
                link_ch = f"https://api.whatsapp.com/send?phone=549{telf}&text={urllib.parse.quote(msg_ch)}"
                
                st.markdown(f"""
                <div class="card-white" style="border-left: 10px solid #27ae60;">
                    <div class="route-txt">🚛 {str(orig).upper()} ➔ {str(dest).upper()}</div>
                    <div>
                        <span class="info-tag">⚙️ {equi}</span>
                        <span class="info-tag">📱 {telf}</span>
                    </div>
                    <a href="{link_ch}" target="_blank" class="btn-wsp" style="background-color: #2c3e50;">CONTACTAR CHOFER</a>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.info("Buscando camiones...")

# --- PANEL DE CONTROL (Borrar) ---
with st.expander("🔐 ADMINISTRADOR (Clave: 1323)"):
    passw = st.text_input("Contraseña", type="password")
    if passw == ADMIN_PASSWORD:
        st.write("⚠️ Para borrar, eliminá la fila en el Google Sheet.")
        c1, c2 = st.columns(2)
        with c1: 
            st.write("**Últimas Cargas (Hoja 5):**")
            st.dataframe(pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}").tail(3))
        with c2:
            st.write("**Últimos Camiones (Hoja 6):**")
            st.dataframe(pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}").tail(3))

st.markdown("<br><center><small>© 2026 RETORNO MATCH</small></center>", unsafe_allow_html=True)
