# 2. ESTILO CSS DEFINITIVO (Fondo Blindado y Transparencias)
st.markdown("""
    <style>
    /* 1. FONDO OBLIGATORIO PARA TODAS LAS CAPAS */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMain"] {
        background: linear-gradient(rgba(0, 0, 0, 0.82), rgba(0, 0, 0, 0.82)), 
                    url('https://images.unsplash.com/photo-1519003722824-192d992a6059?auto=format&fit=crop&w=1920&q=80') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }

    /* 2. HACER TRANSPARENTES LOS CONTENEDORES INTERNOS */
    div[class^="st-emotion-cache"], .main .block-container {
        background-color: transparent !important;
    }

    /* 3. MEJORAR CONTRASTE DE PESTAÑAS (TABS) */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        padding: 10px !important;
        border-radius: 12px !important;
    }
    
    /* 4. TARJETAS CON EFECTO VIDRIO (Para que se vea el fondo atrás) */
    .card {
        background: rgba(255, 255, 255, 0.95); /* Casi blanco pero deja pasar un poco de textura */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    
    .card-camion { border-left: 10px solid #25D366; }
    .card-carga { border-left: 10px solid #3498db; }

    /* Estilos de texto para máxima legibilidad sobre el fondo oscuro */
    h1, h2, h3, p, label {
        color: white !important;
    }
    
    .title-text { color: #1a1a1a !important; font-weight: 800; font-size: 22px; }
    .sub-text { color: #444 !important; }
    </style>
    """, unsafe_allow_html=True)
