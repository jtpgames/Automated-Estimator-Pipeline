import logging
from typing import List

import pandas as pd

from src.database import Database
from src.dto.dtos import EstimatorPipelineDTO
from src.factory.factories import DatabaseFeatureExtractorFactory


class DataPreparation:

    def __init__(self, config: EstimatorPipelineDTO, database: Database):
        self.__feature_names = config.features
        self.__y_column = config.y_column
        self.__db = database

    def get_dataset(self):
        feature_extractors = self.__setup_feature_extractors()
        df = self.__load_data(feature_extractors)
        print("before remove")
        print(df.info())
        df = df[df[self.__y_column] != 0]
        print("after remove")
        print(df.info())
        y = df.pop(self.__y_column)
        return df, y

    def __setup_feature_extractors(self) -> List:
        factory = DatabaseFeatureExtractorFactory()
        extractors = []
        for name in self.__feature_names:
            extractor_class = factory.get(name)
            extractor_object = extractor_class(self.__db, name)
            extractors.append(extractor_object)
        return extractors

    @staticmethod
    def __load_data(extractors) -> pd.DataFrame:
        df = pd.DataFrame()
        for extractor in extractors:
            if df.empty:
                df = extractor.get_df()
            else:
                new_df = extractor.get_df()
                df = pd.merge(
                    df,
                    new_df,
                    how="inner",
                    left_index=True,
                    right_index=True
                )

            logging.info(df.shape)
        return df
