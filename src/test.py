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

@dataclass
class RandomObject:
    name: str
    count: int



test_list = [RandomObject("test", 1), RandomObject("test2", 2)]
print(test_list[0])