import category_encoders
import numpy as np
import pandas as pd
from numpy import uint8
from sklearn.feature_extraction import FeatureHasher
from sqlalchemy import Column, Integer

from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor, AbstractETLFeatureExtractor
)
from src.feature_extractor.encoder.dict_encoder import \
    JSONEncodedDict
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker


class ListParallelRequestsStartAnalysisExtractor(
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

        indices = []
        counter = 0
        for index, col in result_data:
            indices.append(index)
            if len(col) > 0:
                for key, val in col.items():
                    # index in cmd names mapping starts at 1, so minus 1
                    array[int(counter), int(key) - 1] = val
                    counter = counter + 1

        int_cmd_dict = self.get_int_cmd_mapping()
        column_names = ["{}__start".format(name) for name in int_cmd_dict.values()]
        df = pd.DataFrame(array, index=indices, dtype=uint8, columns=column_names)

        return df

class HashListPR1TypesWithCountAnalysisExtractor(AbstractAnalysisFeatureExtractor):

    def get_column(self) -> Column:
        return Column("list_pr_1", JSONEncodedDict)

    def df_post_creation_hook(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def get_df(self) -> pd.DataFrame:
        result_data = self.get_column_data(self.get_column())
        df = self.get_df_from_db_column_data(result_data)

        feature_hasher = FeatureHasher(n_features=10)
        test = feature_hasher.fit_transform(df[self.get_column_name()])
        test_df = pd.DataFrame.sparse.from_spmatrix(test)
        print(test_df)
        return test_df


class ListParallelRequestsStartETLExtractor(AbstractETLFeatureExtractor):
    def get_column(self) -> Column:
        return Column(self.get_feature_name(), JSONEncodedDict)

    def extract_feature(
            self, parallel_commands_tracker: ParallelCommandsTracker, tid: str
    ):
        return parallel_commands_tracker[tid]["listParallelCommandsStart"]

