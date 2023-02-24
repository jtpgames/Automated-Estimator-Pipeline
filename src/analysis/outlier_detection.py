import numpy as np
import pandas as pd

from src.database import Database
from src.dto.dtos import OutlierDetectionDTO
from src.feature_extractor.cmd_extractor import CMDAnalysisExtractor


class OutlierDetection:
    __config: OutlierDetectionDTO

    def __init__(self, config: OutlierDetectionDTO, database: Database):
        self.__config = config
        self.__db = database

    def remove_outliers(self, X: pd.DataFrame, y: pd.Series) -> tuple[pd.DataFrame, pd.Series]:
        if not self.__config.remove_outlier:
            return X, y
        y_column = y.name
        df = X.merge(y, left_index=True, right_index=True)
        if "CMD" == self.__config.outlier_modus:
            delete_cmd_after, df = self.__add_cmd_if_not_present(df)
            df = df[~df.groupby("cmd")[y_column].apply(self.__is_outlier)]
            if delete_cmd_after:
                df.drop("cmd", axis=1, inplace=True)
        else:
            df = df[np.abs(df[y_column] - df[y_column].mean()) <= (
                    self.__config.std_threshold * df[y_column].std())]
        y = df.pop(y_column)
        return df, y

    def get_string_containing_outlier_info(self):
        if self.__config.remove_outlier:
            return "remove_outlier_{}_std_{}".format(self.__config.outlier_modus, self.__config.std_threshold)
        return "containing_outlier"

    def __add_cmd_if_not_present(self, df):
        delete_cmd_after = False
        if "cmd" not in df.columns.values:
            extractor = CMDAnalysisExtractor(self.__db, "cmd")
            new_df = extractor.get_df()
            df = pd.merge(
                df,
                new_df,
                how="inner",
                left_index=True,
                right_index=True
            )
            delete_cmd_after = True
        return delete_cmd_after, df

    def __is_outlier(self, s):
        lower_limit = s.mean() - (s.std() * self.__config.std_threshold)
        upper_limit = s.mean() + (s.std() * self.__config.std_threshold)
        return ~s.between(lower_limit, upper_limit)
