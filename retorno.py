import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="RETORNO MATCH", layout="wide")

# Diseño con el fondo de depósito que te gusta y tarjetas claras
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover; background-attachment: fixed;
    }
    .card { background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; border-left: 10px solid #2ecc71; color: black; }
    .card-camion { border-left: 10px solid #3498db; }
    .card h3 { margin-top:0; color: #1a1a1a; }
    .stButton>button { width: 100%; background-color: #2ecc71; color: white; font-weight: bold; height: 50px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXIÓN DIRECTA (Usamos el link de lectura rápida)
# Para escribir, el usuario usará el formulario nativo
URL = "https://docs.google.com/spreadsheets/d/18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOS/gviz/tq?tqx=out:csv"

def cargar_datos
