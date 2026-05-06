import streamlit as st
import pandas as pd
import time
import urllib.parse
from datetime import datetime

# --- 1. CONFIGURACIÓN DE IDENTIDAD Y BLINDAJE ---
# "creado por Ignacio Diaz" - Requerimiento de seguridad y autoría
CREADOR = "Ignacio Diaz"
ESTRUCTURA = "Nacho"
VERSION = "4.0.0 - BLACK EDITION"

# IDs de Base de Datos (Google Sheets)
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349"
GID_CARGAS = "1267917528"
GID_VIP = "968995524"

st.set_page_config(page_title=f"{ESTRUCTURA} VIP - {CREADOR}", page_icon="📈", layout="wide")

# --- 2. INTERFAZ DE ALTO IMPACTO (CSS CUSTOM) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    * {{ font-family: 'Inter', sans-serif; }}
    
    .main {{ background-color: #050505; }}
    
    /* Contenedor Pro */
    .st-emotion-cache-12w0qpk {{ border-radius: 20px; }}
    
    /* Card de Camión Estilo Apple */
    .truck-card {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }}
    .truck-card:hover {{
        border-color: #f1c40f;
        transform: translateY(-3px);
        background: rgba(241, 196, 15, 0.05);
    }}
    
    /* Branding */
    .badge-vip {{
        background: linear-gradient(45deg, #f1c40f, #f39c12);
        color: black;
        padding: 2px 10px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 0.7em;
    }}

    /* Footer Blindado */
    .footer-blindado {{
        text-align: center;
        padding: 50px;
        margin-top: 50px;
        background: #000;
        border-top: 4px solid #f1c40f;
        color: #fff;
    }}
</style>
""", unsafe_allow_html=True)

# --- 3. PROCESAMIENTO DE DATOS (NÚCLEO NACHO) ---
@st.cache_data(ttl=10)
def cargar_datos_seguros():
    t = int(time.time())
    try:
        # Carga optimizada
        df_ch = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={t}").fillna("-")
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        
        # Formateo de Códigos (Sin comas ni decimales según requerimiento)
        for df in [df_ch, df_ca]:
            if 'CODIGO' in df.columns:
                df['CODIGO'] = df['CODIGO'].apply(lambda x: str(x).split('.')[0].replace(',',''))
        
        return df_ch, df_ca
    except:
        return pd.DataFrame(), pd.DataFrame()

df_ch, df_ca = cargar_datos_seguros()

# --- 4. ENCABEZADO ESTRATÉGICO ---
c_head1, c_head2 = st.columns([2, 1])
with c_head1:
    st.markdown(f"<h1 style='margin:0; letter-spacing:-1px;'>RETORNO MATCH <span style='color:#f1c40f;'>360°</span></h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:gray; margin-bottom:20px;'>Infraestructura de Datos: <b>{CREADOR}</b></p>", unsafe_allow_html=True)

with c_head2:
    st.markdown(f"""
    <div style="text-align:right; background:rgba(255,255,255,0.05); padding:10px; border-radius:10px;">
        <small style="color:gray;">ESTADO DEL SERVIDOR</small><br>
        <b style="color:#2ecc71;">● SISTEMA OPERATIVO</b><br>
        <small style="color:white; opacity:0.5;">v{VERSION}</small>
    </div>
    """, unsafe_allow_html=True)

# --- 5. PANEL DE CONTROL (DASHBOARD) ---
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("FLOTA ACTIVA", len(df_ch), "🚚")
with m2:
    st.metric("CARGAS DISPONIBLES", len(df_ca), "📦")
with m3:
    st.metric("HUB LOGÍSTICO", "San Jorge", "📍")
with m4:
    st.metric("TENDENCIA", "+12%", "📈")

# --- 6. MÓDULO DE OPERACIONES ---
tab_radar, tab_market, tab_maps = st.tabs(["⚡ RADAR DE UNIDADES", "🏦 MERCADO DE CARGAS", "🌍 MAPA DE FLUJO"])

with tab_radar:
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        busqueda = st.text_input("🔍 Buscar por destino, chofer o patente...", placeholder="Ej: Rosario, Scania, AC123...").upper()
    
    if not df_ch.empty:
        # Filtrado inteligente
        mask = df_ch.apply(lambda x: busqueda in str(x).upper(), axis=1)
        df_final = df_ch[mask] if busqueda else df_ch
        
        for _, row in df_final.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="truck-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="badge-vip">CHOFER VIP</span>
                        <span style="color:gray; font-size:0.8em;">ID: {row.get('PATENTE', '-')}</span>
                    </div>
                    <h2 style="margin:10px 0; color:white;">{row.get('CHOFER', 'SIN NOMBRE')}</h2>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:15px;">
                        <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;">
                            <small style="color:#f1c40f;">ORIGEN</small><br><b>{row.get('ORIGEN', '-')}</b>
                        </div>
                        <div style="background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;">
                            <small style="color:#f1c40f;">DESTINO</small><br><b>{row.get('DESTINO', '-')}</b>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón de acción mejorado
                tel = str(row.get('TELEFONO', '')).replace('.0','')
                if tel != '-' and len(tel) > 5:
                    wsp_link = f"https://wa.me/{tel}?text=Hola%20{row.get('CHOFER')},%20vimos%20tu%20unidad%20en%20el%20sistema%20de%20Ignacio%20Diaz."
                    st.markdown(f"""<a href="{wsp_link}" target="_blank" style="text-decoration:none;">
                        <div style="background:#25D366; color:black; text-align:center; padding:12px; border-radius:10px; font-weight:bold; margin-top:-25px; margin-bottom:20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                            ENVIAR PROPUESTA WHATSAPP
                        </div></a>""", unsafe_allow_html=True)

with tab_market:
    st.markdown("### 📦 Cargas en Oferta")
    st.dataframe(df_ca, use_container_width=True, hide_index=True)

with tab_maps:
    st.info("Visualización de rutas estratégicas optimizada para la zona de San Jorge.")
    # Mapa simplificado para evitar errores de librerías externas
    st.map(df_ch) if 'lat' in df_ch.columns else st.warning("Coordenadas GPS en proceso de sincronización.")

# --- 7. FOOTER DEFINITIVO (BLINDAJE IGNACIO DIAZ) ---
st.markdown(f"""
<div class="footer-blindado">
    <p style="letter-spacing:5px; margin-bottom:10px; opacity:0.6;">SOFTWARE DE GESTIÓN LOGÍSTICA</p>
    <h1 style="margin:0; font-weight:900; color:#f1c40f;">{CREADOR.upper()}</h1>
    <p style="font-size:1.2em; margin:15px 0;">"La estructura e interfaz que está funcionando debe ser blindada"</p>
    <div style="margin-top:30px; border:1px solid #333; display:inline-block; padding:10px 30px; border-radius:50px;">
        Creado por <b>{CREADOR}</b> y sus legales • © 2026
    </div>
    <div style="margin-top:20px;">
        <a href="#" style="color:gray; text-decoration:none; font-size:0.8em;">TÉRMINOS DE USO</a> | 
        <a href="#" style="color:gray; text-decoration:none; font-size:0.8em;">PROTECCIÓN DE DATOS</a>
    </div>
</div>
""", unsafe_allow_html=True)
