import sys
from typing import List, Any

import typer
import pandas as pd
from sklearn.ensemble import AdaBoostRegressor
from sklearn.linear_model import (
    LinearRegression,
    Ridge,
    Lasso,
    ElasticNet,
    SGDRegressor,
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor

from src.regression_analysis import CommandNumberMapping
from src.regression_analysis.ConfigurationHandler import ConfigurationHandler
from src.regression_analysis.Database import Database
from src.regression_analysis.features import FeatureExtractors
from src.regression_analysis.features.AbstractFeatureExtractor import (
    AbstractFeatureExtractor,
)
from src.regression_analysis.features.CMDExtractor import CMDExtractor
from src.regression_analysis.features.FeatureExtractors import (
    get_feature_extractors_by_name,
)
from src.regression_analysis.features.FirstCommandEndExtractor import (
    FirstCommandEndExtractor,
)
from src.regression_analysis.features.FirstCommandStartExtractor import (
    FirstCommandStartExtractor,
)
from src.regression_analysis.features.PROneExtractor import PROneExtractor
from src.regression_analysis.features.PRThreeExtractor import PRThreeExtractor
from src.regression_analysis.features.ResponseTimeExtractor import ResponseTimeExtractor

from numpy import std, mean

from src.regression_analysis.models.Models import get_model_objects_from_names


class RegressionAnalysis:
    __db_path: str
    __cmd_numbers_mapping = {}
    __df: pd.DataFrame
    __features_extractors: List[AbstractFeatureExtractor] = []
    __models: List[tuple[str, Any]]
    __db: Database
    __y_column_name: str

    def __init__(self, config_handler: ConfigurationHandler):
        self.__models = get_model_objects_from_names(config_handler.get_models())
        self.__db = Database(config_handler)
        self.__df = pd.DataFrame()
        self.__features_extractors = get_feature_extractors_by_name(
            config_handler.get_features()
        )
        self.__y_column_name = config_handler.get_y_column_name()

    def load_data(self):
        for extractor in self.__features_extractors:
            if self.__df.empty:
                self.__df = extractor.get_df(self.__db, self.__cmd_numbers_mapping)
            else:
                print(self.__df)
                new_df = extractor.get_df(self.__db, self.__cmd_numbers_mapping)
                print(new_df)
                self.__df = pd.merge(
                    self.__df, new_df, how="inner", left_index=True, right_index=True
                )

            print(self.__df.shape)

        print("max values in columns")
        print(self.__df.max())
        self.__remove_outliers()
        print("memory consumption: ", sys.getsizeof(self.__df))

    def __remove_outliers(self):
        anomalies = []
        y = self.__df[self.__y_column_name]

        # Set upper and lower limit to 3 standard deviation
        random_data_std = std(y)
        random_data_mean = mean(y)
        anomaly_cut_off = random_data_std * 3

        lower_limit = random_data_mean - anomaly_cut_off
        upper_limit = random_data_mean + anomaly_cut_off
        # print("Lower Limit {}, Upper Limit {}".format(lower_limit, upper_limit))
        # Generate outliers
        outlier_index = 0
        for outlier in y:
            if outlier > upper_limit or outlier < lower_limit:
                anomalies.append((outlier_index, outlier))
            outlier_index += 1

        # TODO check for perfomance optimization (creating df and then dropping df from original)
        outliers = pd.DataFrame.from_records(anomalies, columns=["Index", "Value"])
        self.__df.drop(outliers["Index"])

    def create_models(self):
        y = self.__df.pop(self.__y_column_name)
        x_train, x_test, y_train, y_test = train_test_split(
            self.__df, y, test_size=0.2, random_state=42
        )

        print("Shapes: X_train:", x_train.shape, " y_train:", y_train.shape)
        print("Shapes: X_test:", x_test.shape, " y_test:", y_test.shape)
        print("X_train")
        print("-------")
        print(x_train)
        print("-------")
        print("X_test")
        print("-------")
        print(x_test)

        print("====")
        print("== Evaluating each model in turn ==")
        results = []
        names = []
        for name, model in self.__models:
            cv_results = cross_val_score(model, x_train, y_train)
            results.append(cv_results)
            names.append(name)
            print(
                "%s: Accuracy: %0.2f (+/- %0.2f)"
                % (name, cv_results.mean(), cv_results.std() * 2)
            )
        print("====")

        # for model in self.__models:
        #     model.fit()

    # def save_models(self):
    #     for model in self.__models:
    #         model.save()


def main(config_file_path: str = "resources/config/analysis_config.json"):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    regression_analysis = RegressionAnalysis(config_handler)
    regression_analysis.load_data()
    regression_analysis.create_models()


if __name__ == "__main__":
    typer.run(main)
