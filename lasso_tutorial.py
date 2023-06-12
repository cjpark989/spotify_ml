import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import Lasso

def dict_2_array(dict):
    npArray = np.array(list(dict.items()))

    return npArray

data = pd.read_csv("data.csv")

# split into X and y var
y = data["popularity"]
X = data[["valence", "acousticness", "tempo", "energy", "liveness", "danceability", "loudness", "speechiness", "instrumentalness", "duration_ms"]]

# split X into X train, X test, Y train, Y test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state = 42)

# build model, optimize hyperparameter and train on training dataset

# scale dataset in advance (use pipeline object in scikit-learn
pipeline = Pipeline([
    ('scaler', StandardScaler()), 
    ('model', Lasso())
])

# optimize the alpha hyperparameter of Lasso regression
search = GridSearchCV(pipeline,
    {'model__alpha':np.arange(0.1, 10, 0.1)},
    cv = 5, 
    scoring = "neg_mean_squared_error", verbose = 3
)

search.fit(X_train,y_train)

coefficients = search.best_estimator_.named_steps['model'].coef_

importance = np.abs(coefficients)
print(importance)