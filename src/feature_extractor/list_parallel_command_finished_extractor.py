import numpy as np
import pandas as pd
from numpy import uint8
from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractFeatureETLExtractor
)
from src.feature_extractor.json_encoder.dict_encoder import \
    JSONEncodedDict
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ListParallelRequestsFinishedAnalysisExtractor(
    AbstractAnalysisFeatureExtractor
):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), Integer)

    def df_postproduction(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def get_df(self) -> pd.DataFrame:
        column = Column(self.get_column_name(), JSONEncodedDict)
        result_data = self.get_column_data(column).all()
        result_mapping = self.get_cmd_names_mapping()

        # TODO warum + 1 ?
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


import json


class ListParallelRequestsFinishedETLExtractor(AbstractFeatureETLExtractor):
    def get_feature_name(self) -> str:
        return "List parallel requests finished"

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return json.dumps(
            parallel_commands_tracker[tid]["listParallelCommandsFinished"]
        )
