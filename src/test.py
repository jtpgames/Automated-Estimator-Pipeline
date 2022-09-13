from re import search

import numpy as np
from marshmallow_dataclass import dataclass
from sklearn import datasets, linear_model
from sklearn.base import TransformerMixin
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sqlalchemy import engine, create_engine
import pandas as pd

def get_timestamp_from_string(line: str):
    return search(r"\s*\d*-\d*-\d*\s\d*:\d*:\d*\.?\d*", line).group().strip()

test_str = "[2020-12-21 00:00:09,165000] (PR:  0/ 1/ 0) ID_REQ_CMD_GETSERVERTIMESTR        : Response time 15 ms"
search_pattern = r"\s*\d*-\d*-\d*\s\d*:\d*:\d*\.?\d*"
search_ret = search(search_pattern, test_str)
print(search_ret.group().strip())
