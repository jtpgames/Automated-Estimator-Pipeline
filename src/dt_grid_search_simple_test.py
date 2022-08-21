import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.datasets import fetch_openml
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.tree import DecisionTreeClassifier

np.random.seed(0)

X, y = fetch_openml("titanic", version=1, as_frame=True, return_X_y=True)

# Alternatively X and y can be obtained directly from the frame attribute:
# X = titanic.frame.drop('survived', axis=1)
# y = titanic.frame['survived']

numeric_features = ["age", "fare"]
numeric_transformer = Pipeline(
    steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)

categorical_features = ["embarked", "sex", "pclass"]
categorical_transformer = OneHotEncoder(handle_unknown="ignore")

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features),
    ]
)

clf = Pipeline(
    steps=[("preprocessor", preprocessor), ("classifier", DecisionTreeClassifier())]
)

criterion = ['gini', 'entropy']
max_depth = [2, 4, 6, 8, 10, 12]
fit_intercept = [True, False]

parameters = dict(
    # linear_reg__fit_intercept=fit_intercept,
    classifier__criterion=criterion,
    classifier__max_depth=max_depth
)


grid_search = GridSearchCV(clf, parameters, n_jobs=-1, verbose=1, scoring=["r2", "neg_root_mean_squared_error"], refit="r2")
grid_search.fit(X, y)

print("model score: %.3f" % grid_search.best_score_)