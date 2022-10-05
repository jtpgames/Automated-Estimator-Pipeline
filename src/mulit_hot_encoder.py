import numpy as np
import pandas as pd
import scipy
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer


class MultiHotEncoder(BaseEstimator, TransformerMixin):
    """Wraps `MultiLabelBinarizer` in a form that can work with `ColumnTransformer`. Note
    that input X has to be a `pandas.DataFrame`.

    Requires the non-training DataFrame to ensure it collects all labels so it won't be lost in train-test-split

    To initialize, you musth pass the full DataFrame and not
    the df_train or df_test to guarantee that you captured all categories.
    Otherwise, you'll receive a user error with regards to missing/unknown categories.
    """

    def __init__(self, classes=None, sparse_output=False):
        self.sparse_output = sparse_output
        self.classes = classes

    def fit(self, X, y=None):
        self.mlbs = list()
        self.n_columns = 0
        # Collect columns

        self.categories_ = self.classes_ = self.classes

        # Loop through columns
        for i in range(X.shape[1]):  # X can be of multiple columns
            mlb = MultiLabelBinarizer(classes=self.classes_, sparse_output=self.sparse_output)
            mlb.fit(X[:, i])
            self.mlbs.append(mlb)
            self.classes_.append(mlb.classes_)
            self.n_columns += 1

        self.categories_ = self.classes_
        return self

    def transform(self, X: pd.DataFrame):
        if self.n_columns == 0:
            raise ValueError('Please fit the transformer first.')
        if self.n_columns != X.shape[1]:
            raise ValueError(f'The fit transformer deals with {self.n_columns} columns '
                             f'while the input has {X.shape[1]}.'
                             )
        result = list()
        for i in range(self.n_columns):
            result.append(self.mlbs[i].transform(X.iloc[:, i]))

        if self.sparse_output:
            result = scipy.sparse.hstack(result)
        else:
            result = np.concatenate(result, axis=1)
        return result

    def fit_transform(self, X: pd.DataFrame, y=None):
        super().fit_transform(X, y)

    def get_feature_names_out(self, input_features=None):
        cats = self.categories_
        if input_features is None:
            input_features = self.columns
        elif len(input_features) != len(self.categories_):
            raise ValueError(
                "input_features should have length equal to number of "
                "features ({}), got {}".format(len(self.categories_),
                                               len(input_features)))

        feature_names = []
        for i in range(len(cats)):
            names = [input_features[i] + "_" + str(t) for t in cats[i]]
            feature_names.extend(names)

        return np.asarray(feature_names, dtype=object)
