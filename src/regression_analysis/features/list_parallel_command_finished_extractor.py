import json

import pandas as pd
from numpy import short

from src.regression_analysis.configuration_handler import ConfigurationHandler
from src.regression_analysis.database import Database
from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)


class ListParallelRequestsFinished(AbstractFeatureExtractor):
    def get_column_name(self) -> str:
        return "List parallel requests finished"

    def get_df(self, db, names_mapping) -> pd.DataFrame:
        df = self.load_df_column_from_db(db)
        print(type(df.iloc[0][0]))
        # print(df.dtypes)
        # print(df)
        # print("---------")
        # print(df)
        # print("---------")
        # print("map to columns")
       #print(df[self.get_column_name()].values.tolist())
        #df = pd.DataFrame(df.pop(self.get_column_name()).values.tolist())
        #print(df)
        # print("add prefix")
        # df = df.add_prefix("last_finished_")
        # print(df)
        # print("---------")
        # print("fillna")
        # df = df.fillna(0)
        # print(df)
        #return df.astype(short, copy=False)


    def __apply_func(self, row, names_mapping):
        command_dict = json.loads(row)
        numerical_dict = {}
        for key, value in command_dict.items():
            numerical_dict["end_list_cmd_{}".format(
                self.get_cmd_int(key, names_mapping)
            )] = value
        return numerical_dict

if __name__ == "__main__":
    config_handler = ConfigurationHandler("resources/config/analysis_config.json")
    config_handler.load_config()
    database = Database(config_handler)
    test = ListParallelRequestsFinished()
    test.get_df(database, {})