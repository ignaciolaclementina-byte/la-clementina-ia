import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN
st.set_page_config(page_title="RETORNO MATCH", layout="centered")

# 2. LINK DE EXCEL VERIFICADO
SHEET_ID = "18oipzHxWlvBPGWOf7ikEnXRh3EeG9IMC06jZG0uLiOs"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# 3. ESTILO VISUAL
st.markdown("""
    <style>
    .stApp { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070"); 
        background-size: cover; 
    }
    h1, h3, p, [data-baseweb="tab"] { color: white !important; font-weight: bold; }
    .card { 
        background: white; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #2ecc71; 
        margin-bottom: 20px; 
    }
