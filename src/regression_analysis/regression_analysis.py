import json
import logging
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import typer
from joblib import dump
# explicitly require this experimental feature
from sklearn.experimental import enable_halving_search_cv  # noqa
from sklearn.feature_selection import f_regression, \
    SelectPercentile, SelectKBest
from sklearn.model_selection import GridSearchCV, KFold
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

# now you can import normally from model_selection

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
handler = logging.StreamHandler(sys.stdout)


class RegressionAnalysis:
    __std_threshold = 3
    __df: pd.DataFrame
    __feature_extractors: List[AbstractAnalysisFeatureExtractor] = []
    __db: Database
    __grid_search_params: dict
    __config_handler: AnalysisConfigurationHandler

    def __init__(
            self,
            config_handler: AnalysisConfigurationHandler,
            db: Database
    ):
        self.__config_handler = config_handler
        self.__db = db
        self.__df = pd.DataFrame()

    def start(self):
        self.setup_feature_extractors()
        self.load_data()
        self.create_models()

    def setup_feature_extractors(self):
        self.__feature_extractors = get_feature_extractors_by_name_analysis(
            self.__db,
            self.__config_handler.get_features()
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

    def create_models(self):
        y = self.__df.pop(self.__config_handler.get_y_column_name())
        steps = self.__add_preprocess_steps()
        steps.append(("estimator", "passthrough"))
        logging.info(self.__df.shape)
        pipe = Pipeline(steps=steps)
        grid_dict = self.__create_grid_search_parameter_dict()
        cv = list(KFold(n_splits=2, shuffle=True, random_state=42).split(self.__df))
        grid_search = GridSearchCV(pipe, grid_dict, **self.__config_handler.get_grid_search_parameter(), cv=cv)

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

    def __remove_outliers(self):
        self.__df = self.__df[
            np.abs(
                self.__df[self.__config_handler.get_y_column_name()] - self.__df[
                    self.__config_handler.get_y_column_name()].mean()
            ) <= (
                    self.__std_threshold * self.__df[
                self.__config_handler.get_y_column_name()].std())]

    def __add_preprocess_steps(self):
        steps = []
        pipeline_parameters = self.__config_handler.get_pipeline_parameters()
        if "feature_selection" in pipeline_parameters:
            if pipeline_parameters["feature_selection"] == "percentile":
                steps.append(
                    ("feature_selection",
                     SelectPercentile(f_regression, percentile=10)), )
            elif pipeline_parameters["feature_selection"] == "kbest":
                steps.append(
                    ("feature_selection",
                     SelectKBest(f_regression, k=30)), )
        if "scaler" in pipeline_parameters and \
                pipeline_parameters["scaler"] == "std":
            steps.append(("std_scaler", StandardScaler()))
        return steps

    def __create_grid_search_parameter_dict(self):
        grid_dict = []
        for wrapper in self.__config_handler.get_estimators():
            wrapper_dict = wrapper.get_parameter()
            new_dict = {"estimator": [wrapper.get_estimator()]}
            for key, val in wrapper_dict.items():
                new_name = "estimator__" + key
                new_dict[new_name] = val
            grid_dict.append(new_dict)
        return grid_dict

    def __save_results(self, grid_search):
        self.__log_results(grid_search)

        path_to_folder = self.__create_folder_for_estimator_saving(grid_search)

        self.__save_estimator(grid_search, path_to_folder)
        self.__save_cmd_names_mapping(path_to_folder)
        self.__save_cv_results(grid_search, path_to_folder)

    def __create_folder_for_estimator_saving(self, grid_search):
        today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        estimator_name = grid_search.best_estimator_.named_steps["estimator"].__class__.__name__
        scores = self.__get_scores_from_cv_result(grid_search.cv_results_)
        folder_name = "{}_{}_{}_{:.2f}".format(today, estimator_name, scores[1][0], scores[0][0])
        path_to_folder = Path(
            self.__config_handler.get_model_save_path()
        ) / folder_name
        os.makedirs(path_to_folder, exist_ok=True)
        return path_to_folder

    def __save_cv_results(self, grid_search, path_to_folder):
        df = pd.DataFrame.from_records(grid_search.cv_results_)
        logging.info("save cv results")
        mapping_name = "cv_results.xlsx"
        path_to_mapping_file = Path(path_to_folder) / mapping_name
        df.to_excel(path_to_mapping_file)
        log_file_name = "infos.txt"
        path_to_log_file = Path(path_to_folder) / log_file_name
        log_file = open(path_to_log_file, "w")
        estimator_name = grid_search.best_estimator_.named_steps["estimator"].__class__.__name__
        scores = self.__get_scores_from_cv_result(grid_search.cv_results_)
        score_str = ""
        for counter in range(len(scores[0])):
            score_str = score_str + "{}: {:02f} ".format(scores[1][counter], scores[0][counter])
        log_file.write(
            "{}: Metrics: {}".format(
                estimator_name, score_str
            )
        )
        column_names = ", ".join(self.__df.columns.values)
        estimators_string = " ".join([str(elem) for elem in self.__config_handler.get_estimators()])
        log_file.write("\ndataframe columns: {}".format(column_names))
        log_file.write("\ndatabase limit: {}".format(self.__config_handler.get_db_limit()))
        log_file.write("\nbest_parameter: {}".format(grid_search.best_params_))
        log_file.write("\npipeline: {}".format(self.__config_handler.get_pipeline_parameters()))
        log_file.write("\nestimators: {}".format(estimators_string))
        log_file.close()

    def __get_scores_from_cv_result(self, cv_results):
        grid_params = self.__config_handler.get_grid_search_parameter()
        # if multiple scoring metrices are defined, refit has to be set
        params = {}
        if "refit" in grid_params:
            params = {
                "key": "rank_test_" + grid_params["refit"],
                "values": ["mean_test_" + x for x in grid_params["scoring"]],
                "names": grid_params["scoring"]
            }
        else:
            # if refit is not set, then scoring has to be a single value
            params = {"key": "rank_test_score", "values": ["mean_test_score"],
                      "names": [grid_params["scoring"]]}

        df = pd.DataFrame.from_records(cv_results)
        scores = df[df[params["key"]] == 1][params["values"]].mean().values
        names = params["names"]
        return scores, names

    def __save_cmd_names_mapping(self, path_to_folder):
        logging.info("save cmd names mapping")
        mapping_name = "cmd_names_mapping.json"
        path_to_mapping_file = Path(path_to_folder) / mapping_name
        with open(path_to_mapping_file, "w") as file:
            json.dump(self.__db.get_cmd_int_dict(), file)

    def __save_estimator(
            self,
            grid_search,
            path_to_folder
    ):
        estimator_name = grid_search.best_estimator_.named_steps["estimator"].__class__.__name__
        dump_file_name = "{}_model.joblib".format(estimator_name)
        path_to_dump_file = Path(path_to_folder) / dump_file_name
        logging.info("dump file {}".format(path_to_dump_file))
        dump(grid_search.best_estimator_, path_to_dump_file)

    def __log_results(self, grid_search):
        logging.info("best_parameter: {}".format(grid_search.best_params_))
        logging.info("best_score: {}".format(grid_search.best_score_))
        if self.__config_handler.use_feature_selection():
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


def main(
        config_file_path: str = "resources/config/analysis_config.json"
):
    config_handler = AnalysisConfigurationHandler(config_file_path)
    config_handler.load_config()
    database = Database(config_handler)

    regression_analysis = RegressionAnalysis(config_handler, database)
    regression_analysis.start()


if __name__ == "__main__":
    typer.run(main)
