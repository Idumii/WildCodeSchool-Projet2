import streamlit as st
import pandas as pd

import streamlit as st


st.image("image_data_analyse.png", width=150)

st.title("Analyse des données")
st.write("Après notre étude de marché sur la consommation de cinéma dans la région de la Creuse, nous avons réalisé une analyse approndie de la base de données pour identifier les tendances et les préférences des spectateurs. ")
st.write("Ci-dessous, les étapes suivies.")

st.subheader("Pré-filtrage des données")
st.write("Avant de faire l'analyse, nous avons pré-filtré les données pour réduire notre jeu de données à ~14000 lignes :")
st.write("- Suppression des genres : Documentary / Short / News / Talk-show / Game-Show / Reality-TV / Adult,")
st.write("- Affichage des films avec avec au minimum une productrion française, américaine ou britannique,")