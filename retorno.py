for c in st.session_state.cargas:
        with st.container():
            # Tarjeta de información
            st.markdown(f"""
            <div class='card-carga'>
                <strong style='font-size: 20px;'>📍 {c['origen']} → San Jorge</strong><br>
                <span>📦 Carga: {c['item']}</span><br>
                <strong style='color: #2E7D32 !important; font-size: 18px;'>PAGO: ${c['pago']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Link de WhatsApp directo (SIEMPRE VISIBLE)
            msg = f"🚛 *RETORNO MATCH*\nMe interesa la carga de *{c['item']}* desde *{c['origen']}* hacia San Jorge. ¿Sigue disponible?"
            link_wa = f"https://wa.me/543406649346?text={urllib.parse.quote(msg)}"
            
            # Botón verde directo
            st.markdown(f"""
                <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 12px; border-radius: 25px; text-align: center; font-weight: bold; margin-top: -10px; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3);">
                        📲 CONTACTAR POR WHATSAPP
                    </div>
                </a>
            """, unsafe_allow_html=True)
