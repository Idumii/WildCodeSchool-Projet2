import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder, FunctionTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder

# Fonction pour alourdir la valeur des colonnes
def multiply_block(X, factor):
    return X * factor

# Custom transformer for MultiLabelBinarizer
class MultiLabelBinarizerPipelineFriendly(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.mlb = MultiLabelBinarizer()

    def fit(self, X, y=None):
        self.mlb.fit(X)
        return self

    def transform(self, X):
        return self.mlb.transform(X)

    def get_feature_names_out(self, input_features=None):
        return self.mlb.classes_

# Preprocessor pour standardiser les colonnes numériques
preprocessor = ColumnTransformer(
    transformers=[
        ('actors', Pipeline([
            ('mlb', MultiLabelBinarizerPipelineFriendly()),
            ('weight', FunctionTransformer(lambda x: multiply_block(x, 2))),
            ]), 'actors'),
        ('directors', Pipeline([
            ('mlb', MultiLabelBinarizerPipelineFriendly()),
            ('weight', FunctionTransformer(lambda x: multiply_block(x, 0.8))),
            ]), 'directors'),
        ('genres', MultiLabelBinarizerPipelineFriendly(), 'genres'),
        ('decade', Pipeline([
            ('encoder', OrdinalEncoder()),
            ('weight', FunctionTransformer(lambda x: multiply_block(x, 0.5))),
            ]), ['decade']),
        ('scaler', StandardScaler(), ['averageRating']),
        ('numVotes', Pipeline([
            ('scaler', StandardScaler()),
            ('weight', FunctionTransformer(lambda x: multiply_block(x, 0.2))),
            ]), ['numVotes'])
    ]
)

# Pipeline complet
pipeline = Pipeline(
    steps=[
        ('preprocessor', preprocessor),
        ('knn', NearestNeighbors(n_neighbors=11))
    ]
)

def find_neighbors(df, pipeline, titre):
    """
    Trouve les voisins les plus proches d'un film donné.
    
    Args:
        df (pd.DataFrame): Le DataFrame contenant les données des films.
        pipeline (Pipeline): Le pipeline entraîné.
        titre (str): Le titre du film à rechercher.
    
    Returns:
        pd.DataFrame: Les voisins les plus proches avec leurs informations.
    """
    film_cible = df[df['frenchTitle'].str.contains(titre, case=False, na=False)]
    if film_cible.empty:
        return None, f"Film '{titre}' non trouvé."

    idx_film = film_cible.index[0]
    film_non_standardise = df.drop(columns=['frenchTitle']).loc[[idx_film]]
    film_transforme = pipeline.named_steps['preprocessor'].transform(film_non_standardise)
    distances, indices = pipeline.named_steps['knn'].kneighbors(film_transforme)

    neighbor_original_indices = df.iloc[indices[0]].index
    neighbor_info = df.loc[neighbor_original_indices][['frenchTitle', 'averageRating', 'numVotes', 'decade', 'genres', 'actors', 'directors']]
    return neighbor_info, f"Film trouvé : {df.loc[idx_film, 'frenchTitle']}"