import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de página
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# --- CONEXIÓN ---
ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL_CARGAS = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=cargas"
URL_CAMIONES = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet=camiones"

# --- DISEÑO Y ESTILOS ---
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    .card { 
        background: white; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 8px solid #2ecc71; 
        margin-bottom: 15px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    h1, h2, h3, p, label { color: white !important; font-weight: bold; }
    .card b, .card
