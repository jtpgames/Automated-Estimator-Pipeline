from typing import List, Any

from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    SGDRegressor,
)
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor

possible_models = [
    ("LR", LinearRegression()),
    ("Ridge", Ridge()),
    ("Lasso", Lasso()),
    ("ElasticNet", ElasticNet()),
    ("DT", DecisionTreeRegressor()),
    ("SGD", SGDRegressor(verbose=1)),
    ("MLP", MLPRegressor(verbose=1, learning_rate_init=0.01, early_stopping=True)),
    ("KNN", KNeighborsRegressor(weights="distance")),
    ("AdaLR", AdaBoostRegressor(LinearRegression(), n_estimators=10)),
    ("AdaDT", AdaBoostRegressor(DecisionTreeRegressor(), n_estimators=10)),
]


def get_model_objects_from_names(model_names: List[str]) -> List[tuple[str, Any]]:
    models: List[tuple[str, Any]] = []
    for name in model_names:
        for x, model in possible_models:
            if name == x:
                models.append((name, model))

    return models
