from joblib import load
from sklearn2pmml import sklearn2pmml, make_pmml_pipeline

test = load("DecisionTreeRegressor_model.joblib")
pipeline = make_pmml_pipeline(test)

sklearn2pmml(pipeline, "real_25_low_dt.pmml", True)

