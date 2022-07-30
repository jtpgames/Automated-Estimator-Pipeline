import numpy as np
import pandas as pd
from numpy import uint8
from sqlalchemy import Column, Integer

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
from src.regression_analysis.features.json_encoder.dict_encoder import \
    JSONEncodedDict


class ListParallelRequestsStart(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "List parallel requests start"

    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)

    def df_postproduction(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        column = Column(self.get_column_name(), JSONEncodedDict)
        result_data = db.get_training_data_from_db(column).all()
        result_mapping = db.get_names_mapping_from_db().all()
        array = np.zeros(
            shape=(len(result_data), len(result_mapping) + 1),
            dtype=uint8
        )

        for index, col in result_data:
            if len(col) > 0:
                for key, val in col.items():
                    array[int(index), int(key)] = val

        df = pd.DataFrame(array, dtype=uint8)
        return df
