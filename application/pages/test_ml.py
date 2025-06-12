import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from machineLearning.ml_utils import pipeline, find_neighbors

# Chargement des données
df = pd.read_csv('../../ressources/df_ml.csv', sep=';', encoding='utf-8')
pipeline.fit(df.drop(columns=['frenchTitle']))

# Interface Streamlit
st.title("Recherche de films similaires")
titre = st.text_input("Entrez le titre du film :")

if titre:
    neighbors, message = find_neighbors(df, pipeline, titre)
    st.write(message)
    if neighbors is not None:
        st.dataframe(neighbors)