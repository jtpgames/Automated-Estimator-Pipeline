import numpy as np
from dask.distributed import Client

import joblib
from memory_profiler import profile
from sklearn.datasets import load_digits
from sklearn.model_selection import RandomizedSearchCV
from sklearn.svm import SVC


@profile
def run():
    client = Client(processes=False)  # create local cluster

    digits = load_digits()

    param_space = {
        'C': np.logspace(-6, 6, 13),
        'gamma': np.logspace(-8, 8, 17),
        'tol': np.logspace(-4, -1, 4),
        'class_weight': [None, 'balanced'],
    }

    model = SVC(kernel='rbf')
    search = RandomizedSearchCV(model, param_space, cv=5, n_iter=100, verbose=10)

    with joblib.parallel_backend('dask'):
        search.fit(digits.data, digits.target)


if __name__ == "__main__":
    run()
