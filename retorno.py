import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse
from datetime import datetime
import math

# --- 1. CONFIGURACIÓN (ESTRUCTURA BLINDADA - CREADO POR IGNACIO DIAZ) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CARGAS = "1267917528"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"
ADMIN_PIN = "1323" 

# --- 2. CARGA DE DATOS SEGUROS ---
@st.cache_data(ttl=5) 
def cargar_datos_seguros():
    try:
        t = int(time.time())
        df_ca = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={t}").fillna("-")
        # Filtrar borrados si existen
        if not df_ca.empty:
            mask = df_ca.astype(str).apply(lambda x: x.str.contains('BORRADO', case=False)).any(axis=1)
            df_ca = df_ca[~mask]
        return df_ca
    except:
        return pd.DataFrame()

df_ca_raw = cargar_datos_seguros()

# --- 3. FUNCIONES AUXILIARES ---
def limpiar_wsp(num):
    clean = "".join(filter(str.isdigit, str(num)))
    if not clean: return "5491111111111"
    if clean.startswith("0"): clean = clean[1:]
    if clean.startswith("15"): clean = clean.replace("15", "", 1)
    return "549" + clean if not clean.startswith("549") else clean

def ocultar_telefono(num):
    clean = "".join(filter(str.isdigit, str(num)))
    return f"*******{clean[-4:]}" if len(clean) > 4 else "*******"

# --- 4. INTERFAZ Y ESTILOS ---
st.set_page_config(page_title="RETORNO MATCH VIP - COSECHA", page_icon="🌾", layout="wide")

if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False

st.markdown("""
<style>
    .stApp { background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075') !important; background-size: cover !important; background-attachment: fixed !important; }
    .card-cosecha { background: #e8f5e9 !important; border: 2px solid #2e7d32 !important; color: #1b5e20; border-radius: 15px; padding: 20px; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .btn-wsp { background-color: #2e7d32; color: white !important; padding: 12px; border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; transition: 0.3s; }
    .btn-wsp:hover { background-color: #1b5e20; transform: scale(1.02); }
    h3 { color: #2e7d32; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🌾 OPERATIVO ARRIME COSECHA</h1>", unsafe_allow_html=True)

# --- 5. PANEL ADMINISTRADOR (SOLO IGNACIO DIAZ) ---
if st.session_state.admin_mode:
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        st.markdown("<h4 style='color:white;'>📢 Publicar Nuevo Arrime</h4>", unsafe_allow_html=True)
        with st.form("f_arr", clear_on_submit=False):
            z_loc = st.text_input("📍 Zona (Ej: San Jorge)")
            g_det = st.text_input("🌾 Detalle (Ej: Maíz a Planta)")
            t_val = st.text_input("💰 Tarifa")
            w_arr = st.text_input("📱 WhatsApp de contacto")
            
            submit = st.form_submit_button("✅ GUARDAR Y GENERAR TEXTO")
            
            if submit:
                # 1. Guardar en Google Sheets
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA", 
                    "entry.170847116": z_loc, 
                    "entry.576675281": f"ARRIME|{g_det}|{t_val}", 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w_arr
                })
                st.success("¡Datos publicados en la web!")
                
                # 2. Generar texto para COPIAR Y PEGAR en el Canal
                texto_para_canal = (
                    f"🌾 *NUEVO OPERATIVO DE ARRIME*\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"📍 *ZONA:* {z_loc}\n"
                    f"📝 *DETALLE:* {g_det}\n"
                    f"💰 *TARIFA:* {t_val}\n\n"
                    f"🚛 *ANOTARSE AQUÍ:* \n"
                    f"https://retorno-match-sanjorge.streamlit.app/\n\n"
                    f"✅ _Gestionado por Ignacio Diaz_"
                )
                
                st.markdown("---")
                st.markdown("📋 **COPIÁ ESTE TEXTO PARA TU CANAL:**")
                # El componente .code incluye el botón de "Copy" automático
                st.code(texto_para_canal, language="text")
                st.info("Pega este texto directamente en tu Canal de WhatsApp.")
                st.cache_data.clear()

    main_col = col_a2
else:
    # Si no es admin, usa todo el ancho para mostrar los arrimes
    main_col = st.container()

# --- 6. VISTA DE LOS ARRIMES (PÚBLICO) ---
with main_col:
    if not df_ca_raw.empty:
        # Filtrar solo las filas que son de tipo ARRIME
        df_arrime = df_ca_raw[df_ca_raw.astype(str).apply(lambda x: x.str.contains('ARRIME', case=False)).any(axis=1)]
        
        if df_arrime.empty:
            st.markdown("<p style='color:white; text-align:center;'>No hay operativos vigentes en este momento.</p>", unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, (idx, r) in enumerate(df_arrime.iterrows()):
                if len(r) < 5: continue
                # Texto para el botón de contacto individual
                texto_contacto = urllib.parse.quote(f"Hola, me contacto por el arrime en {r[2]} ({r[3]}) visto en la web.")
                
                with cols[i % 2]:
                    st.markdown(f'''
                        <div class="card-cosecha">
                            <h3>📍 {r[2]}</h3>
                            <b>DETALLE:</b> {r[3]}<br>
                            <b>TARIFA:</b> {r[3].split('|')[-1] if '|' in r[3] else 'Consultar'}<br>
                            <b>TEL:</b> {ocultar_telefono(r[4])}<br><br>
                            <a href="https://api.whatsapp.com/send?phone={limpiar_wsp(r[4])}&text={texto_contacto}" target="_blank" class="btn-wsp">🚜 POSTULARME</a>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Opción de borrar solo para Admin
                    if st.session_state.admin_mode:
                        if st.button(f"🗑️ Quitar {i}", key=f"del_{idx}"):
                            requests.post(URL_CARGAS_POST, data={"entry.610070407": "BORRADO", "entry.576675281": f"REF:{r[0]}"})
                            st.cache_data.clear()
                            st.rerun()

# --- 7. PIE DE PÁGINA (LEGALES) ---
st.markdown(f"""
<br><br><hr>
<center style='color:rgba(255,255,255,0.6);'>
    <p style='font-size:18px; font-weight:bold; color:white;'>Creado por Ignacio Diaz</p>
    © 2026 RETORNO MATCH VIP - Todos los derechos reservados.
</center>
""", unsafe_allow_html=True)

# --- 8. ACCESO ADMIN ---
with st.expander("⚙️ ACCESO ADMINISTRADOR"):
    pass_input = st.text_input("Introduce el PIN para publicar:", type="password")
    if pass_input == ADMIN_PIN:
        st.session_state.admin_mode = True
        st.success("Modo Edición Activo")
    elif pass_input != "":
        st.error("PIN Incorrecto")
