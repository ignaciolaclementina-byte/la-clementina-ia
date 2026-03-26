# ... (Mantenemos toda la estructura de configuración inicial de Ignacio Diaz)

if st.session_state.admin_mode:
    col_a1, col_a2 = st.columns([1, 2.2])
    with col_a1:
        st.markdown("<h4 style='color:white;'>📢 Cargar Nuevo Arrime</h4>", unsafe_allow_html=True)
        with st.form("f_arr", clear_on_submit=True):
            z_loc = st.text_input("📍 Zona")
            g_det = st.text_input("🌾 Detalle")
            t_val = st.text_input("💰 Tarifa")
            w_arr = st.text_input("📱 WhatsApp de contacto")
            
            submit = st.form_submit_button("✅ GUARDAR EN WEB")
            
            if submit:
                # 1. Guardar en Google Sheets
                requests.post(URL_CARGAS_POST, data={
                    "entry.610070407": "ARRIME ZONA", 
                    "entry.170847116": z_loc, 
                    "entry.576675281": f"ARRIME|{g_det}|{t_val}", 
                    "entry.1930562861": "COSECHA", 
                    "entry.466540450": w_arr
                })
                st.success("¡Guardado en la web!")
                
                # 2. Generar el mensaje para el CANAL
                mensaje_canal = (
                    f"🌾 *NUEVO OPERATIVO DE ARRIME*\n"
                    f"━━━━━━━━━━━━━━━━━━\n\n"
                    f"📍 *ZONA:* {z_loc}\n"
                    f"📝 *DETALLE:* {g_det}\n"
                    f"💰 *TARIFA:* {t_val}\n\n"
                    f"🚛 *POSTULATE AQUÍ:* \n"
                    f"https://retorno-match-sanjorge.streamlit.app/\n\n"
                    f"✅ _Gestionado por Ignacio Diaz_"
                )
                
                texto_url = urllib.parse.quote(mensaje_canal)
                link_canal = f"https://api.whatsapp.com/send?text={texto_url}"
                
                # Mostramos un botón gigante para enviarlo al canal
                st.markdown(f"""
                    <div style="background:#25D366; padding:15px; border-radius:10px; text-align:center;">
                        <a href="{link_canal}" target="_blank" style="color:white; text-decoration:none; font-weight:bold; font-size:18px;">
                            📲 TOCÁ AQUÍ PARA ENVIAR AL CANAL
                        </a>
                    </div>
                """, unsafe_allow_html=True)
                
                st.cache_data.clear()

# ... (El resto del código de visualización sigue igual)
