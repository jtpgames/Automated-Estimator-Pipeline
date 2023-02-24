import pandas as pd
import numpy as np
import category_encoders as ce


def test_func():
    categories = ["a", "b", "c", "d", "e", "f"]

    samples = 5
    # data = {
    #     "cat": [categories[x] for x in np.random.randint(0, 6, samples)],
    #     "feature_1": [x for x in np.random.randint(10, 20, samples)],
    #     "feature_2": [x for x in np.random.randint(10, 20, samples)],
    #     "feature_3": [x for x in np.random.randint(10, 20, samples)],
    #     "target": [x for x in np.random.randint(5, 10, samples)],
    # }
    data = {
        "cat": [{"a":1, "b":3},{"b":4},{"c":4},{"d":4},{"e":4}],
        "feature_1": [x for x in np.random.randint(10, 20, samples)],
        "feature_2": [x for x in np.random.randint(10, 20, samples)],
        "feature_3": [x for x in np.random.randint(10, 20, samples)],
        "target": [x for x in np.random.randint(5, 10, samples)],
    }

    df = pd.DataFrame.from_dict(data)

    hash_encode = ce.HashingEncoder(cols=["cat"])
    test = hash_encode.fit_transform(df)
    print(test.info())


