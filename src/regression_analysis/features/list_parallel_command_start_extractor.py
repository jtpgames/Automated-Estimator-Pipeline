import json

import pandas as pd
from numpy import short

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class ListParallelRequestsStart(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "List parallel requests start"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        df = self.load_df_column_from_db(db)
        df.add_prefix("list_start_")
        df.join(pd.DataFrame(df.pop(self.get_column_name()).values.tolist()))
        df.fillna(0)
        print(df)
        return df.astype(short, copy=False)

    def __apply_func(self, row, names_mapping):
        command_dict = json.loads(row)
        numerical_dict = {}
        for key, value in command_dict.items():
            numerical_dict["start_list_cmd_{}".format(
                self.get_cmd_int(key, names_mapping)
            )] = value
        return numerical_dict
