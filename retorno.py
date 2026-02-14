# ==========================================
# PESTAÑA 2: SOY EMPRESA (Vista Detallada)
# ==========================================
with tab_empresa:
    col_a, col_b = st.columns([1, 2.2])
    with col_a:
        st.markdown("### 🏢 Publicar Carga")
        # ... (mantener tu formulario de carga igual)
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

                # Mapeo exacto según tu última captura de Excel (image_3df483.png)
                # r[1]:Origen, r[2]:Destino, r[3]:Equipo, r[4]:WhatsApp, r[5]:CUIT, r[6]:LINTI, r[7]:Link, r[8]:ESTADO
                
                estado_val = str(r[8]).upper()
                is_verif = "VERIFICADO" in estado_val
                badge = '<div class="badge-verif">✅ CHOFER VERIFICADO</div>' if is_verif else '<div class="badge-verif" style="color:#888; border-color:#888;">⏳ PENDIENTE</div>'
                color_borde = '#2ecc71' if is_verif else '#3498db'

                st.markdown(f"""
                <div class="card-white" style="border-left-color: {color_borde};">
                    {badge}
                    <div class="route-txt">🚛 {r[1]} ➔ {r[2]}</div>
                    <hr style="margin: 10px 0; border: 0.5px solid #eee;">
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 15px;">
                        <div>⚙️ <b>EQUIPO:</b><br>{r[3]}</div>
                        <div>📱 <b>WHATSAPP:</b><br>{r[4]}</div>
                        <div>🆔 <b>CUIT TRANSPORTE:</b><br>{r[5]}</div>
                        <div>💳 <b>LINTI / CARNET:</b><br>{r[6]}</div>
                    </div>
                    
                    <div style="margin-top: 15px; background: #f8f9fa; padding: 10px; border-radius: 8px; font-size: 13px; color: #666;">
                        ℹ️ <i>Revisá la documentación antes de contratar. El sello verificado indica que el CUIT y LINTI coinciden con el transporte.</i>
                    </div>

                    <div style="display:flex; gap:10px; margin-top: 15px;">
                        <a href="https://api.whatsapp.com/send?phone=549{r[4]}" target="_blank" class="btn-wsp" style="flex:2; margin-top:0;">💬 HABLAR CON CHOFER</a>
                        <a href="{r[7]}" target="_blank" class="btn-wsp" style="background:#3498db; flex:1; margin-top:0;">📂 VER PAPELES</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        except: st.info("Cargando camiones...")
