import json
from abc import ABC
from ast import literal_eval

import pandas as pd
from numpy import uint8
from sqlalchemy import select, types, MetaData, Table, Column, Integer, String
import numpy as np

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class JSONEncodedDict(types.TypeDecorator):
    impl = types.TEXT

    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        return literal_eval(value)


class ListParallelRequestsStart(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "List parallel requests start"

    def get_df(self, db, names_mapping) -> pd.DataFrame:

        metadata_obj = MetaData()
        data = Table(
            'gs_training_data', metadata_obj,
            Column('index', Integer, primary_key=True),
            Column('List_parallel_requests_start', JSONEncodedDict),
        )
        names_mapping = Table(
            'gs_training_cmd_mapping', metadata_obj,
            Column('index', Integer, primary_key=True),
            Column('mapping', String),
        )

        con = db.connection()

        mapping_query = select(names_mapping)
        mapping_result = con.execute(mapping_query).scalars().all()

        data_query = select(data)
        data_result = con.execute(data_query).all()

        array = np.zeros(
            shape=(len(data_result), len(mapping_result) + 1),
            dtype=uint8
        )

        for index, col in data_result:
            if len(col) > 0:
                for key, val in col.items():
                    array[int(index), int(key)] = val

        df = pd.DataFrame(array, dtype=uint8)
        return df
