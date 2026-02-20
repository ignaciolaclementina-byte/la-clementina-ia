import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN (Tus links reales) ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    
ADMIN_PASSWORD = "1323" 

# URLs de envío (Actualizadas según tus links de pre-llenado)
URL_CHOFERES_POST = "https://docs.google.com/forms/d/e/1FAIpQLSdCrbuhvT00W26YxDzCIJ35CN0jbBtKtVf1Dl7zUghT7OIrBA/formResponse"
URL_CARGAS_POST = "https://docs.google.com/forms/d/e/1FAIpQLSeTdWp-0x3p4lSsdNe7ceOZReoaEYj1WeoVovf93CnTkDHXGw/formResponse"

st.set_page_config(page_title="RETORNO MATCH", page_icon="🚛", layout="wide")

# --- 2. ESTILOS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                        url('https://images.unsplash.com/photo-1519003722824-194d4455a60c?q=80&w=2075&auto=format&fit=crop') !important;
        background-size: cover !important; background-attachment: fixed !important;
    }
    .stTabs [data-baseweb="tab"] {
        flex: 1; height: 70px !important; background-color: #2c3e50 !important;
        border-radius: 12px !important; color: white !important; font-size: 18px !important;
        font-weight: 900 !important; margin: 5px; border: 1px solid #34495e !important;
    }
    .stTabs [aria-selected="true"] { background-color: #3498db !important; }
    .card-white {
        background: white !important; border-radius: 15px; padding: 20px; margin-bottom: 15px;
        border-left: 10px solid #3498db; color: #333; box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    .route-txt { font-size: 22px; font-weight: 900; color: #1e3799; text-transform: uppercase; }
    .btn-wsp { 
        background-color: #25D366; color: white !important; padding: 12px; 
        border-radius: 10px; text-decoration: none; font-weight: bold; display: block; text-align: center; margin-top: 10px;
    }
    .badge-verif { color: #2ecc71; font-weight: 900; font-size: 14px; border: 2px solid #2ecc71; padding: 4px 10px; border-radius: 20px; float: right; }
    .footer { text-align: center; color: white; opacity: 0.8; padding: 40px; font-size: 14px; margin-top: 50px; border-top: 0.5px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; color:white;'>🚛 RETORNO MATCH</h1>", unsafe_allow_html=True)

# --- BUSCADORES ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with c_b2: b_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# --- PESTAÑA 1: SOY CHOFER (Busca Cargas) ---
with tab_chofer:
    col_i, col_d = st.columns([1, 2.2])
    with col_i:
        st.markdown("### 📢 Publicar mi Camión")
        with st.form("form_ch", clear_on_submit=True):
            o = st.text_input("📍 Ubicación Actual")
            d = st.text_input("🏁 Destino")
            e = st.selectbox("🚛 Equipo", ["Chasis", "Semi", "Sider", "Acoplado", "Batea", "Térmico"])
            w = st.text_input("📱 WhatsApp (Ej: 3406441234)")
            cuit = st.text_input("🆔 CUIT")
            linti = st.text_input("💳 N° LINTI")
            link_doc = st.text_input("📂 Link Documentación")
            if st.form_submit_button("PUBLICAR CAMIÓN"):
                data = {
                    "entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e,
                    "entry.1542650763": cuit, "entry.1837643722": linti, 
                    "entry.769375120": link_doc, "entry.1574172378": w
                }
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            # Sincronización con la columna "Origen" (Columna 1)
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                # Filtros
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                msg_ch = urllib.parse.quote(f"*RETORNO MATCH*\nMe interesa la carga: {r[1]} a {r[2]}")
                st.markdown(f"""
                <div class="card-white" style="border-left-color: #3498db;">
                    <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                    <div style="margin: 10px 0;">
                        <b>📦 CARGA:</b> {r[3]} | <b>⏳ SALE:</b> {r[5]}<br>
                        <b>🏢 EMPRESA:</b> {r[4]}
                    </div>
                    <a href="https://api.whatsapp.com/send?phone=549{r[6]}&text={msg_ch}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando cargas en el sistema...")

# --- PESTAÑA 2: SOY EMPRESA (Busca Camiones) ---
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("form_em", clear_on_submit=True):
            eo = st.text_input("📍 Origen")
            ed = st.text_input("🏁 Destino")
            ec = st.text_input("📦 Mercadería")
            en = st.text_input("Nombre Empresa")
            ef = st.selectbox("⏳ Cuándo", ["Sale hoy", "Mañana", "A convenir"])
            ew = st.text_input("📱 WhatsApp Empresa")
            if st.form_submit_button("SUBIR CARGA"):
                payload_e = {
                    "entry.610070407": eo, "entry.170847116": ed, "entry.576675281": ec,
                    "entry.1930562861": en, "entry.1064058502": ef, "entry.466540450": ew
                }
                requests.post(URL_CARGAS_POST, data=payload_e)
                st.success("✅ Carga publicada"); time.sleep(1); st.rerun()

    with col_b:
        st.markdown("### 🚛 Camiones Disponibles")
        try:
            df_h = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CHOFERES}&t={int(time.time())}").fillna("-")
            for _, r in df_h.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue

                is_verif = "VERIFICADO" in str(r[8]).upper()
                badge = '<div class="badge-verif">✅ VERIFICADO</div>' if is_verif else '<div class="badge-verif" style="color:#888; border-color:#888;">⏳ PENDIENTE</div>'
                st.markdown(f"""
                <div class="card-white" style="border-left-color: {'#2ecc71' if is_verif else '#f1c40f'};">
                    {badge}
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <div style="font-size:14px; margin-top:5px; color:#444;">
                        <b>⚙️ EQUIPO:</b> {r[3]}<br>
                        <b>🆔 CUIT:</b> {r[4]} | <b>💳 LINTI:</b> {r[5]}
                    </div>
                    <div style="display:flex; gap:10px;">
                        <a href="https://api.whatsapp.com/send?phone=549{r[7]}" target="_blank" class="btn-wsp" style="flex:2;">💬 HABLAR CON CHOFER</a>
                        <a href="{r[6]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 PAPELES</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Sincronizando con Excel...")

# --- PANEL DE CONTROL ---
st.markdown("---")
with st.expander("🛠️ PANEL DE CONTROL (ADMIN)"):
    pw = st.text_input("Contraseña admin", type="password")
    if pw == ADMIN_PASSWORD:
        st.subheader("✅ Gestión de Verificaciones")
        st.write("Para validar, escribí 'VERIFICADO' en la columna I del Excel.")
        url_edit = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid={GID_CHOFERES}"
        st.markdown(f'<a href="{url_edit}" target="_blank" style="background:#2ecc71; color:white; padding:10px 20px; border-radius:10px; text-decoration:none; font-weight:bold;">ABRIR EXCEL PARA VALIDAR</a>', unsafe_allow_html=True)
    elif pw != "": st.error("Clave incorrecta")

st.markdown(f'<div class="footer"><p>© 2026 <b>RETORNO MATCH</b> - San Jorge, Santa Fe</p><p>Creado por <b>Ignacio Díaz</b></p></div>', unsafe_allow_html=True)
