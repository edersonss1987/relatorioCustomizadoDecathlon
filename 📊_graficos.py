import streamlit as st
import datetime
import requests

from main import *


agora = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# =======================
# SIDEBAR PERSONALIZADA
# =======================
with st.sidebar:
    st.image("assets\Decathlon_Logo.png")
    st.markdown("---")
    st.sidebar.write('DATA ATUAL')
    st.sidebar.write(agora)

    
st.write("olá")
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()
st.sidebar.divider()

with aba2:
    teve_acesso_de_saida_hoje.head(10)
