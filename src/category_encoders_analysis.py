from multiprocessing import freeze_support

import category_encoders as ce
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sqlalchemy import Column, Integer, Float

from src.modified_db import ModifiedDatabase


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
response_time_column = Column("response_time", Float)
result = db.get_training_data_cursor_result_columns(
    [cmd_column, pr_1_column, pr_2_column, pr_3_column,
     response_time_column])
df = db.get_df_from_db_column_data(result,
                                   ["cmd", "pr_1", "pr_2", "pr_3",
                                    "response_time"])

# remove outlier
indecies_to_del = df.index[df.groupby("cmd")["response_time"].apply(is_outlier)].to_list()
df = df.drop(index=indecies_to_del)

y = df.pop("response_time")
X = df


# pipeline

pipe = Pipeline(steps=[("ordinal_encoder", ce.HashingEncoder(cols=["cmd"], max_process=1)),("lin_reg", LinearRegression())])
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.3)

pipe.fit(X_train, y_train)
score = pipe.score(X_test, y_test)
print(score)
