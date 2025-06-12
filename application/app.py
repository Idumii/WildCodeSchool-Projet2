import streamlit as st
import pandas as pd
import os
import sys
print("test")
# Ajoute le chemin absolu vers le dossier racine du projet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.api.api_utils import *

st.set_page_config(
    page_title="Accueil",
    page_icon="👋",
)

st.write("# Page de base 👋")

st.sidebar.success("Choisir une page au-dessus.")

# Affichage des films les mieux notés par décennie
options = [
    "1970", "1980", "1990", "2000", "2010", "2020"
]
selection = st.pills(
    "Sélectionner une décennie",
    options=options,
    selection_mode="single",
    default=options[0],
)


movies_decade = get_top_movies_decade(
    decade=int(selection),
    page_count=1
)


# On va afficher les films dans 5 colonnes
if movies_decade:
    st.write(f"## Films les mieux notés des années {selection}s")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if len(movies_decade) > 0:
            st.write(f"### {movies_decade[0]['frenchTitle']} ({movies_decade[0]['startYear']})")
            if movies_decade[0].get('poster_path'):
                st.image(movies_decade[0]['poster_path'], width=200)
    with col2:
        if len(movies_decade) > 1:
            st.write(f"### {movies_decade[1]['frenchTitle']} ({movies_decade[1]['startYear']})")
            if movies_decade[1].get('poster_path'):
                st.image(movies_decade[1]['poster_path'], width=200)
    with col3:
        if len(movies_decade) > 2:
            st.write(f"### {movies_decade[2]['frenchTitle']} ({movies_decade[2]['startYear']})")
            if movies_decade[2].get('poster_path'):
                st.image(movies_decade[2]['poster_path'], width=200)
    with col4: 
        if len(movies_decade) > 3:
            st.write(f"### {movies_decade[3]['frenchTitle']} ({movies_decade[3]['startYear']})")
            if movies_decade[3].get('poster_path'):
                st.image(movies_decade[3]['poster_path'], width=200)
    with col5:
        if len(movies_decade) > 4:
            st.write(f"### {movies_decade[4]['frenchTitle']} ({movies_decade[4]['startYear']})")
            if movies_decade[4].get('poster_path'):
                st.image(movies_decade[4]['poster_path'], width=200)
else:
    st.write("Aucun film trouvé pour cette décennie.")