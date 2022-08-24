from sklearn.datasets import load_iris
from sklearn import tree
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

iris = load_iris()
X, y = iris.data, iris.target

X_train, X_test, y_train, y_test = train_test_split(X,y, random_state=42, test_size=0.5)

est = DecisionTreeRegressor()
est_2 = DecisionTreeRegressor()
select = SelectFromModel(estimator=est)
pipeline = Pipeline(steps=[("feature_selection", select), ("estimator", est)])
parameter_grid = {"estimator": DecisionTreeRegressor()}
#grid_search = GridSearchCV(pipeline, )
pipeline.fit(X_train,y_train)
y_pred = pipeline.predict(X_test)
r2_score = r2_score(y_test, y_pred)
print(r2_score)