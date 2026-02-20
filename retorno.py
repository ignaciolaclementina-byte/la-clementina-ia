import streamlit as st
import pandas as pd
import time
import requests
import urllib.parse

# --- 1. CONFIGURACIÓN ---
SHEET_ID = "18oipzHxWlvBPGW0f7ikEnXRh3EeG9IMC06jZG0uLiOs"
GID_CHOFERES = "1392659349" 
GID_CARGAS = "1267917528"    
ADMIN_PASSWORD = "1323" 

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

# --- BUSCADORES Y REFRESH ---
c_b1, c_b2, c_act = st.columns([2, 2, 1])
with c_b1: b_origen = st.text_input("🔍 FILTRAR ORIGEN:").strip()
with c_b2: b_destino = st.text_input("🏁 FILTRAR DESTINO:").strip()
with c_act:
    st.write("<br>", unsafe_allow_html=True)
    if st.button("🔄 ACTUALIZAR", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

tab_chofer, tab_empresa = st.tabs(["🚀 SOY CHOFER", "🏢 SOY EMPRESA"])

# ==========================================
# PESTAÑA 1: SOY CHOFER
# ==========================================
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
            linti = st.text_input("💳 N° LINTI / Carnet")
            link_doc = st.text_input("📂 Link Documentación (Drive/Foto)")
            if st.form_submit_button("PUBLICAR"):
                data = {
                    "entry.1304806144": o, "entry.1519265625": d, "entry.597193898": e,
                    "entry.1574172378": w, "entry.1542650763": cuit, 
                    "entry.1837643722": linti, "entry.769375120": link_doc
                }
                requests.post(URL_CHOFERES_POST, data=data)
                st.success("✅ ¡Publicado!"); time.sleep(1); st.rerun()

    with col_d:
        st.markdown("### 📦 Cargas Disponibles")
        try:
            df_c = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_CARGAS}&t={int(time.time())}").fillna("-")
            for _, r in df_c.iloc[::-1].iterrows():
                if b_origen and b_origen.lower() not in str(r[1]).lower(): continue
                if b_destino and b_destino.lower() not in str(r[2]).lower(): continue
                
                # MENSAJE POTENCIADO CHOFER -> EMPRESA
                msg_ch = urllib.parse.quote(
                    f"*RETORNO MATCH* 🚛💨\n"
                    f"----------------------------\n"
                    f"Hola! Me interesa la *CARGA* que publicaste:\n"
                    f"📍 *ORIGEN:* {r[1]}\n"
                    f"🏁 *DESTINO:* {r[2]}\n"
                    f"📦 *MERCADERÍA:* {r[3]}\n\n"
                    f"¿Sigue disponible? Soy chofer y estoy listo para cargar."
                )
                
                st.markdown(f"""
                <div class="card-white">
                    <div class="route-txt">📍 {r[1]} ➔ {r[2]}</div>
                    <div style="margin: 10px 0;"><b>📦 CARGA:</b> {r[3]} | 🏢 <b>EMPRESA:</b> {r[5]}</div>
                    <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg_ch}" target="_blank" class="btn-wsp">💬 CONSULTAR CARGA</a>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Buscando cargas...")

# ==========================================
# PESTAÑA 2: SOY EMPRESA
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        with st.form("form_em", clear_on_submit=True):
            eo, ed, ec, en = st.text_input("📍 Origen"), st.text_input("🏁 Destino"), st.text_input("📦 Carga"), st.text_input("Empresa")
            ef, ew = st.selectbox("⏳ Cuándo", ["Hoy", "Mañana", "A convenir"]), st.text_input("📱 WhatsApp")
            if st.form_submit_button("SUBIR CARGA"):
                requests.post(URL_CARGAS_POST, data={"entry.610070407":eo,"entry.170847116":ed,"entry.576675281":ec,"entry.1930562861":en,"entry.1064058502":ef,"entry.466540450":ew})
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
                
                # MENSAJE POTENCIADO EMPRESA -> CHOFER
                msg_em = urllib.parse.quote(
                    f"*RETORNO MATCH* 🏢🤝\n"
                    f"----------------------------\n"
                    f"Hola! Vi tu *CAMIÓN* disponible en la App:\n"
                    f"🛣️ *RUTA:* {r[1]} ➔ {r[2]}\n"
                    f"⚙️ *EQUIPO:* {r[3]}\n"
                    f"🆔 *CUIT:* {r[5]}\n"
                    f"💳 *LINTI:* {r[6]}\n\n"
                    f"Tengo una carga disponible que te puede interesar. ¿Podemos hablar?"
                )

                st.markdown(f"""
                <div class="card-white" style="border-left-color: {'#2ecc71' if is_verif else '#3498db'};">
                    {badge}
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <div style="font-size:14px; margin-top:5px; color:#444;">
                        <b>⚙️ EQUIPO:</b> {r[3]}<br>
                        <b>🆔 CUIT:</b> {r[5]} | <b>💳 LINTI:</b> {r[6]}
                    </div>
                    <div style="display:flex; gap:10px;">
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}&text={msg_em}" target="_blank" class="btn-wsp" style="flex:2;">💬 HABLAR CON CHOFER</a>
                        <a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1;">📂 PAPELES</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Actualizando lista de camiones...")

# --- FOOTER ---
st.markdown(f'<div class="footer"><p>© 2026 <b>RETORNO MATCH</b> - San Jorge, Santa Fe</p><p>Creado por <b>Ignacio Díaz</b></p></div>', unsafe_allow_html=True)
