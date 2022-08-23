import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import typer
from joblib import dump
from numpy import std, mean
from sklearn.base import BaseEstimator
from sklearn.feature_selection import f_regression, \
    SelectPercentile, SelectKBest
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from typing import List

from src.configuration_handler import AnalysisConfigurationHandler
from src.database import Database
from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor,
)
from src.feature_extractor.feature_extractor_init import \
    get_feature_extractors_by_name_analysis

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
handler = logging.StreamHandler(sys.stdout)


class RegressionAnalysis:
    __std_threshold = 3
    __db_path: str
    __df: pd.DataFrame
    __feature_extractors: List[AbstractAnalysisFeatureExtractor] = []
    __feature_extractor_names = List[str]
    __estimator_wrapper = []
    __pipeline_parameters: dict
    __db: Database
    __y_column_name: str
    __grid_search_params: dict
    __config_handler: AnalysisConfigurationHandler

    def __init__(
            self,
            config_handler: AnalysisConfigurationHandler,
            db: Database
    ):
        self.__estimator_wrapper = config_handler.get_estimators()
        self.__config_handler = config_handler
        self.__db = db
        self.__df = pd.DataFrame()
        self.__feature_extractor_names = config_handler.get_features()
        self.__y_column_name = config_handler.get_y_column_name()
        self.__export_path = config_handler.get_model_save_path()
        self.__grid_search_params = config_handler.get_grid_search_parameter()
        self.__pipeline_parameters = config_handler.get_pipeline_parameters()

    def start(self):
        self.setup_feature_extractors()
        self.load_data()
        self.create_models()

    def setup_feature_extractors(self):
        self.__feature_extractors = get_feature_extractors_by_name_analysis(
            self.__db,
            self.__feature_extractor_names
        )

    def load_data(self):
        logging.info(
            "number feature extractors: {}".format(
                len(self.__feature_extractors)
            )
        )
        for extractor in self.__feature_extractors:
            logging.info(
                "Loading values of extractor: {}".format(
                    extractor.get_column_name()
                )
            )
            if self.__df.empty:
                self.__df = extractor.get_df()
            else:
                new_df = extractor.get_df()
                self.__df = pd.merge(
                    self.__df,
                    new_df,
                    how="inner",
                    left_index=True,
                    right_index=True
                )

            logging.info(self.__df.shape)

        self.__remove_outliers()
        logging.info("memory consumption: {}".format(sys.getsizeof(self.__df)))

    def __remove_outliers(self):
        self.__df = self.__df[
            np.abs(
                self.__df[self.__y_column_name] - self.__df[
                    self.__y_column_name].mean()
                ) <= (
                    self.__std_threshold * self.__df[
                self.__y_column_name].std())]

    def __add_preprocess_steps(self):
        steps = []

        if "feature_selection" in self.__pipeline_parameters:
            if self.__pipeline_parameters["feature_selection"] == "percentile":
                steps.append(
                    ("feature_selection",
                     SelectPercentile(f_regression, percentile=10)), )
            elif self.__pipeline_parameters["feature_selection"] == "kbest":
                steps.append(
                    ("feature_selection",
                     SelectKBest(f_regression, k=30)), )
        if "scaler" in self.__pipeline_parameters and \
                self.__pipeline_parameters["scaler"] == "std":
            steps.append(("std_scaler", StandardScaler()))
        return steps

    def create_models(self):
        y = self.__df.pop(self.__y_column_name)
        steps = self.__add_preprocess_steps()
        steps.append(("estimator", BaseEstimator()))

        pipe = Pipeline(steps=steps)
        grid_dict = self.__create_grid_search_parameter_dict()
        grid_search = GridSearchCV(pipe, grid_dict, **self.__grid_search_params)

        start_time = datetime.now()
        grid_search.fit(self.__df, y)
        end_time = datetime.now()
        delta = end_time - start_time

        logging.info(
            "gridsearch fit call duration in minutes: {}".format(
                delta.seconds / 60
            )
        )

        self.__save_results(grid_search)

    def __save_results(self, grid_search):
        logging.info("best_parameter: {}".format(grid_search.best_params_))
        logging.info("best_score: {}".format(grid_search.best_score_))
        featurelist = list(self.__df.columns.values)
        skb_step = grid_search.best_estimator_.named_steps["feature_selection"]
        feature_scores = ['%.2f' % elem for elem in skb_step.scores_]
        feature_scores_pvalues = ['%.3f' % elem for elem in skb_step.pvalues_]
        features_selected_tuple = [(featurelist[i + 1], feature_scores[i],
                                    feature_scores_pvalues[i]) for i in
                                   skb_step.get_support(indices=True)]
        features_selected_tuple = sorted(
            features_selected_tuple, key=lambda
                    feature: float(feature[1]), reverse=True
        )
        logging.info(' ')
        logging.info('Selected Features, Scores, P-Values')
        logging.info(features_selected_tuple)
        # TODO get name of estimator
        self.__save_estimator(grid_search.best_estimator_, "test")
        self.__save_cmd_names_mapping()
        self.__save_cv_results(grid_search)

    def __save_cv_results(self, grid_search):
        df = pd.DataFrame.from_records(grid_search.cv_results_)
        logging.info("save cv results")
        today = datetime.now().strftime("%Y-%m-%d")
        mapping_name = "cv_results_{}.xlsx".format(today)
        path_to_mapping_file = Path(self.__export_path) / mapping_name
        df.to_excel(path_to_mapping_file)

    def __create_grid_search_parameter_dict(self):
        grid_dict = []
        for wrapper in self.__estimator_wrapper:
            wrapper_dict = wrapper.get_parameter()
            new_dict = {"estimator": [wrapper.get_estimator()]}
            for key, val in wrapper_dict.items():
                new_name = "estimator__" + key
                new_dict[new_name] = val
            grid_dict.append(new_dict)
        return grid_dict

    def __save_cmd_names_mapping(self):
        logging.info("save cmd names mapping")
        today = datetime.now().strftime("%Y-%m-%d")
        mapping_name = "cmd_names_mapping_{}.json".format(today)
        path_to_mapping_file = Path(self.__export_path) / mapping_name
        with open(path_to_mapping_file, "w") as file:
            json.dump(self.__db.get_cmd_int_dict(), file)

    def __save_estimator(
            self,
            pipeline,
            estimator_name,
            mae=0,
            mse=0,
            r_2_score=0
    ):
        today = datetime.now().strftime("%Y-%m-%d")
        log_file_name = "{}_statistics_{}.txt".format(estimator_name, today)
        dump_file_name = "{}_model_{}.joblib".format(estimator_name, today)
        path_to_dump_file = Path(self.__export_path) / dump_file_name
        path_to_log_file = Path(self.__export_path) / log_file_name
        logging.info("dump file {}".format(path_to_dump_file))
        dump(pipeline, path_to_dump_file)
        log_file = open(path_to_log_file, "w")
        log_file.write(
            "{name}: Accuracy: mae {mae:.3f} mse {mse:.2f} r2 score {r_2_score:.2%})".format(
                name=estimator_name, mae=mae,
                mse=mse, r_2_score=r_2_score
            )
        )
        column_names = ", ".join(self.__df.columns.values)
        log_file.write("\ndataframe columns: {}".format(column_names))
        log_file.close()


def main(
        config_file_path: str = "resources/config/analysis_grid_search_config.json"
):
    config_handler = AnalysisConfigurationHandler(config_file_path)
    config_handler.load_config()
    database = Database(config_handler)

    regression_analysis = RegressionAnalysis(config_handler, database)
    regression_analysis.start()


if __name__ == "__main__":
    typer.run(main)
