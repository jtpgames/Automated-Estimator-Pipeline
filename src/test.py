import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import TruncatedSVD, SparsePCA
from sklearn.model_selection import ShuffleSplit, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.tree import DecisionTreeRegressor
from sqlalchemy import Column, Integer, Float

from modified_db import ModifiedDatabase


def is_outlier(s):
    lower_limit = s.mean() - (s.std() * 3)
    upper_limit = s.mean() + (s.std() * 3)
    return ~s.between(lower_limit, upper_limit)


db = ModifiedDatabase(number_rows=500000)

# cmd, list_pr_1, list_pr_2, list_pr_3
cmd_column = Column("cmd", Integer)
pr_1_column = Column("pr_1", Integer)
pr_2_column = Column("pr_2", Integer)
pr_3_column = Column("pr_3", Integer)
list_pr_1_column = Column("hash_list_type_pr_1", Integer)
list_pr_2_column = Column("hash_list_type_pr_2", Integer)
list_pr_3_column = Column("hash_list_type_pr_3", Integer)
response_time_column = Column("response_time", Float)
result = db.get_training_data_cursor_result_columns(
    [cmd_column, pr_1_column, pr_2_column, pr_3_column,
     list_pr_1_column, list_pr_2_column, list_pr_3_column,
     response_time_column])
df = db.get_df_from_db_column_data(result,
                                   ["cmd", "pr_1", "pr_2", "pr_3",
                                    "hash_list_type_pr_1", "hash_list_type_pr_2", "hash_list_type_pr_3",
                                    "response_time"])

# remove outlier
indecies_to_del = df.index[df.groupby("cmd")["response_time"].apply(is_outlier)].to_list()
df = df.drop(index=indecies_to_del)

y = df.pop("response_time")
X = df

# print("get list pr 1")
# extractor = ListPR1Extractor(db)
# list_pr_1_df = extractor.get_df()
# cleaned_list_pr_1_df = list_pr_1_df.drop(index=indecies_to_del)
# print("cleaned df")
# print(cleaned_list_pr_1_df.info())
# X_pr_1_coo = scipy.sparse.coo_matrix(cleaned_list_pr_1_df)
# del cleaned_list_pr_1_df
#
# print("get list pr 3")
# extractor3 = ListPR3Extractor(db)
# list_pr_3_df = extractor.get_df()
# cleaned_list_pr_3_df = list_pr_3_df.drop(index=indecies_to_del)
# print("cleaned df")
# print(cleaned_list_pr_3_df.info())
# X_pr_1_2_coo = scipy.sparse.hstack((X_pr_1_coo, scipy.sparse.coo_matrix(cleaned_list_pr_3_df)))
# del cleaned_list_pr_3_df

# X_coo = scipy.sparse.coo_matrix(X)

# # remove response time equals 0
# df = df[df["response_time"] != 0]

cv = ShuffleSplit(n_splits=2, random_state=42, test_size=0.2)
numeric_transformer = StandardScaler()
categorical_transformer = OneHotEncoder(drop="first", handle_unknown="ignore", sparse=True)
# test = categorical_transformer.fit_transform(X[['cmd']])
print(df)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, ["pr_1", "pr_2", "pr_3"
            , "hash_list_type_pr_1", "hash_list_type_pr_2", "hash_list_type_pr_3"
                                      ]),
        ("cat", categorical_transformer, ["cmd"]),
        # ("hash", FeatureHasher(n_features=20)), ["list_pr_1", "list_pr_3"]
        # ("hash", HashingVectorizer(), ["list_pr_1", "list_pr_3"])
    ])
# test = preprocessor.fit_transform(df)
# fh = FeatureHasher(n_features=20, input_type="string")
# test = fh.fit_transform(df[["list_pr_1", "list_pr_3"]])

# X_coo = preprocessor.fit_transform(X)
# X_coo = scipy.sparse.hstack((X_pr_1_2_coo, X_coo))
pipeline = Pipeline(
    steps=[("pre", preprocessor), ("svd", "passthrough"), ("pca", "passthrough"),
           ("est", DecisionTreeRegressor())])
# best_parm = {"best__score_func": [f_regression, mutual_info_regression], "best__k": np.arange(3, 100, 2)}
svd_param = {"svd": [TruncatedSVD()], "svd__n_components": np.arange(4, 30, 2)}
pca_param = {"pca": [SparsePCA()], "pca__n_components": np.arange(20, 200, 10)}
# param_grid = [svd_param, pca_param]
param_grid = {}
grid_search = GridSearchCV(estimator=pipeline, cv=cv, param_grid=param_grid, verbose=50, refit=False,
                           error_score="raise")
print("start fit")
grid_search.fit(X, y)
print(grid_search.cv_results_)
# df = pd.DataFrame.from_records(grid_search.cv_results_)
# mapping_name = "cv_results_100000.xlsx"
# path_to_mapping_file = mapping_name
# df.to_excel(path_to_mapping_file)

# multi_label_binarizer = MultiHotEncoder(sparse_output=True)
# multi_label_binarizer = MultiLabelBinarizer(sparse_output=True)
# cat_sparse = categorical_transformer.fit_transform(df["cmd"].to_numpy().reshape(-1, 1))
# print(getsizeof(df2))
#
# bin_sparse = multi_label_binarizer.fit_transform(df["list_pr_1"])
# y = df["response_time"]
# # X_sparse = hstack(cat_sparse, bin_sparse)
# pipe = Pipeline(steps=[("estimator", LinearRegression())])
# pipe.fit(X_sparse, y)
# print("model score: %.3f" % pipe.score(X_sparse, y))

# preprocessor = ColumnTransformer(
#     transformers=[("cat", categorical_transformer, ["cmd"]), ("bin", multi_label_binarizer, "list_pr_1")])
# df = preprocessor.fit_transform(df)
# print(getsizeof(df))


# clf = Pipeline(steps=[("preprocessor", preprocessor), ("regressor", LinearRegression())])
#
# X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
# clf.fit(X_train, y_train)
# print("model score: %.3f" % clf.score(X_test, y_test))
