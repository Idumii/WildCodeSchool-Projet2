import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Accueil",
    page_icon="👋",
)

st.write("# Page de base 👋")

df_display = pd.read_csv('../ressources/df_display.csv', sep=';', encoding='utf-8')
print(df_display.head())

st.sidebar.success("Choisir une page au-dessus.")


pd.read_csv