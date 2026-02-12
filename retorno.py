import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# 1. CONFIGURACIÓN Y EL FONDO QUE TE GUSTABA
st.set_page_config(page_title="RETORNO MATCH", layout="wide", page_icon="🚛")

st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
        url("https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?q=80&w=2070");
        background-size: cover;
        background-attachment: fixed;
    }
    
    /* Estilo de las tarjetas para que resalten sobre el fondo */
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        color: black;
        border
