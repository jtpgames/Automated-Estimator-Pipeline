import json
from ast import literal_eval

import pandas as pd
from numpy import short

from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class ListParallelRequestsFinished(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "List parallel requests finished"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        df = self.load_df_column_from_db(db)
        df_preprossed = df[self.get_column_name()].apply(literal_eval)
        df_preprossed = pd.DataFrame(df_preprossed[self.get_column_name()].values.tolist(), index=df.index)
        print(df_preprossed.head())
        preprocessed_df = pd.DataFrame(df[self.get_column_name()].apply(
            self.__apply_func,
            args=(names_mapping,)
        ))
        print(preprocessed_df.head())
        df2 = pd.json_normalize(preprocessed_df[self.get_column_name()])
        df2 = df2.fillna(0)
        df2.astype(short, copy=False)
        return df2

    def __apply_func(self, row, names_mapping):
        command_dict = json.loads(row)
        numerical_dict = {}
        for key, value in command_dict.items():
            numerical_dict["end_list_cmd_{}".format(
                self.get_cmd_int(key, names_mapping)
            )] = value
        return numerical_dict
