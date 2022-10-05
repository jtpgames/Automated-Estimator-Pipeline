import json

import numpy as np
import pandas as pd
from numpy import uint8
from sqlalchemy import Column

from src.feature_extractor.abstract_feature_extractor import AbstractAnalysisFeatureExtractor, \
    AbstractETLFeatureExtractor
from src.feature_extractor.json_encoder.dict_encoder import JSONEncodedDict
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ListParallelRequestsEndAnalysisExtractor(
    AbstractAnalysisFeatureExtractor
):
    def get_column(self) -> Column:
        return Column(self.get_column_name(), JSONEncodedDict)

    def df_post_creation_hook(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def get_df(self) -> pd.DataFrame:
        result_data = self.get_column_data(self.get_column())
        result_mapping = self.get_cmd_names_mapping()

        array = np.zeros(
            shape=(len(result_data), len(result_mapping)),
            dtype=uint8
        )

        for index, col in result_data:
            if len(col) > 0:
                for key, val in col.items():
                    # index in cmd names mapping starts at 1, so minus 1
                    array[int(index), int(key) - 1] = val

        int_cmd_dict = self.get_int_cmd_mapping()
        column_names = ["{}__end".format(name) for name in int_cmd_dict.values()]
        df = pd.DataFrame(array, dtype=uint8, columns=column_names)

        return df


class ListParallelRequestsEndETLExtractor(AbstractETLFeatureExtractor):
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return json.dumps(
            parallel_commands_tracker[tid]["listParallelCommandsEnd"]
        )


class HashListPR2TypesETLExtractor(AbstractETLFeatureExtractor):
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        arr = [int(x) for x in parallel_commands_tracker[tid]["listParallelCommandsEnd"].keys()]
        return hash(frozenset(arr))


class HashListPR2TypesWithCountETLExtractor(AbstractETLFeatureExtractor):
    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        arr = [(int(key), value) for key, value in parallel_commands_tracker[tid]["listParallelCommandsEnd"].items()]
        return hash(frozenset(arr))
