import numpy as np
import pandas as pd
from numpy import uint8, uint16
from sqlalchemy import Column

from feature_extractor.json_encoder.dict_encoder import JSONEncodedDict
from modified_db import ModifiedDatabase


class ListPR1Extractor:
    def __init__(self, db: ModifiedDatabase):
        self.db = db

    def get_column(self) -> Column:
        return Column("list_pr_1", JSONEncodedDict)

    def get_df(self) -> pd.DataFrame:
        result_data = self.db.get_training_data_cursor_result_columns([self.get_column()])
        int_cmd_dict = self.db.get_cmd_mapping(cmd_key=False)

        # print(f"result_data:{len(result_data)} cmd_dict:{len(int_cmd_dict)}")
        array = np.zeros(
            shape=(len(result_data), len(int_cmd_dict)),
            dtype=uint16
        )

        counter = 0
        for index, col in result_data:
            if len(col) > 0:
                for key, val in col.items():
                    # print(f"index:{index} col:{col} key:{key} val:{val}")
                    # index in cmd names mapping starts at 1, so plus 1
                    array[int(counter), int(key) - 1] = val
            counter = counter + 1

        column_names = ["{}__start".format(name) for name in int_cmd_dict.values()]
        df = pd.DataFrame(array, dtype=uint8, columns=column_names)

        return df


class ListPR3Extractor:
    def __init__(self, db: ModifiedDatabase):
        self.db = db

    def get_column(self) -> Column:
        return Column("list_pr_3", JSONEncodedDict)

    def get_df(self) -> pd.DataFrame:
        result_data = self.db.get_training_data_cursor_result_columns([self.get_column()])
        int_cmd_dict = self.db.get_cmd_mapping(cmd_key=False)

        array = np.zeros(
            shape=(len(result_data), len(int_cmd_dict)),
            dtype=uint16
        )
        counter = 0
        for index, col in result_data:
            if len(col) > 0:
                for key, val in col.items():
                    # index in cmd names mapping starts at 1, so plus 1
                    array[int(counter), int(key) - 1] = val
            counter = counter + 1
        print(array)
        column_names = ["{}__finished".format(name) for name in int_cmd_dict.values()]
        df = pd.DataFrame(array, dtype=uint8, columns=column_names)

        return df
