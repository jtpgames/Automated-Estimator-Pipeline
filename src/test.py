import numpy as np
from sklearn import datasets, linear_model
from sklearn.base import TransformerMixin
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sqlalchemy import engine, create_engine
import pandas as pd

'''
outlier detection:
1. group by cmd
2. std per cmd type
3. remove all entries >= 3* std per cmd type
'''
con = create_engine('sqlite:///C:/Users/lierm/IdeaProjects/logfile_analysis/resources/export/db/trainingdata_2022-09'
                    '-02.db')
result = pd.read_sql_table('gs_training_data', con, chunksize=100000)
df = next(result)
df = df[["cmd", "response time"]]
#df = df[df["cmd"].map(df["cmd"].value_counts()) >= 2]
def is_outlier(s):
    lower_limit = s.mean() - (s.std() * 3)
    upper_limit = s.mean() + (s.std() * 3)
    return ~s.between(lower_limit, upper_limit)

#print(df[np.abs(df["response time"] - df["response time"].mean()) <= (3 * df["response time"].std())])

df = df[~df.groupby('cmd')['response time'].apply(is_outlier)]
print(df)
