import streamlit as st
import google.generativeai as genai
from PIL import Image
import urllib.parse

# 1. TUS DOS CLAVES DE API (SISTEMA DE RESPALDO)
CLAVES = [
    "AIzaSyD5BdXRFneGeQn9sG2qHip65dauBNbzKVw",
    "AIzaSyDxGWtHwsXp_dzsg6YnnU7OmPFBCU-_nEU"
]

st.set_page_config(page_title="La Clementina IA", layout="centered")

# 2. DISEÑO Y TRADUCCIONES (CSS LIMPIO)
st.markdown("""
<style>
.stApp {
    background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                      url("https://images.unsplash.com/photo-1594751439417-df9a97693661?q=80&w=2070&auto=format&fit=crop");
    background-size: cover;
}
.titulo { color: white; text-align: center; font-size: 30px; font-weight: bold; text-shadow: 2px 2px 4px black; }

/* TRADUCCIÓN DE BOTONES POR CSS */
section[data-testid="stFileUploadDropzone"] button::after { content: "BUSCAR IMAGEN"; font-size: 14px !important; }
section[data-testid="stFileUploadDropzone"] span { display: none; }
div[data-testid="stCameraInput"] button::after { content: "TOMAR FOTO"; font-size: 14px !important;
