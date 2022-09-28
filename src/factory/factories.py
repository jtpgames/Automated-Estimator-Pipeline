from typing import Any

from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_selection import SelectFromModel, SelectKBest, SelectPercentile
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, SGDRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

possible_estimators = [
    ("LR", LinearRegression),
    ("Ridge", Ridge),
    ("Lasso", Lasso),
    ("DT", DecisionTreeRegressor),
    ("ElasticNet", ElasticNet),
    ("RF", RandomForestRegressor),
    ("SGDR", SGDRegressor)
]


def get_estimater_class_from_name(estimator_name: str) -> Any:
    for x, estimator in possible_estimators:
        if estimator_name == x:
            return estimator
    # TODO raise error
    return None


possible_actions = [
    ("std", StandardScaler),
    ("pca", PCA),
    ("select_from_model", SelectFromModel),
    ("k_best", SelectKBest),
    ("percentile", SelectPercentile)
]


def get_action_class_from_name(action_name: str):
    for x, action in possible_actions:
        if action_name == x:
            return action
    # TODO raise error
    return None
