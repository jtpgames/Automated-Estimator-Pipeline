import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import typer
from joblib import dump, parallel_backend
from numpy import std, mean
from sklearn import tree
from sklearn.feature_selection import SelectKBest, f_regression, \
    SelectPercentile, mutual_info_regression
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor
from typing import List, Any

from src.configuration_handler import AnalysisConfigurationHandler
from src.database import Database
from src.feature_extractor.abstract_feature_extractor import (
    AbstractAnalysisFeatureExtractor,
)
from src.feature_extractor.feature_extractor_init import \
    get_feature_extractors_by_name_analysis
from src.regression_analysis.models.models import get_model_objects_from_names

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
handler = logging.StreamHandler(sys.stdout)
NUM_OF_JOBS = os.environ.get("SLURM_CPUS_PER_TASK")
if NUM_OF_JOBS == None:
    NUM_OF_JOBS = 5

NUM_OF_JOBS = int(NUM_OF_JOBS)


class RegressionAnalysis:
    __db_path: str
    __df: pd.DataFrame
    __feature_extractors: List[AbstractAnalysisFeatureExtractor] = []
    __feature_extractor_names = List[str]
    __models: List[tuple[str, Any]]
    __db: Database
    __y_column_name: str

    def __init__(
            self,
            config_handler: AnalysisConfigurationHandler,
            db: Database
    ):
        self.__models = get_model_objects_from_names(
            config_handler.get_models()
        )
        self.__db = db
        self.__df = pd.DataFrame()
        self.__feature_extractor_names = config_handler.get_features()
        self.__y_column_name = config_handler.get_y_column_name()
        self.__export_path = config_handler.get_model_save_path()

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
        # TODO test with min number of entries per class
        # logging.info(self.__df)
        # self.__df = self.__df.loc[:, (self.__df.sum(axis=0) > 10)]
        # logging.info(self.__df)
        logging.info("memory consumption: {}".format(sys.getsizeof(self.__df)))

    # TODO mit dataframe command ersetzen
    def __remove_outliers(self):
        anomalies = []
        y = self.__df[self.__y_column_name]

        # Set upper and lower limit to 3 standard deviation
        random_data_std = std(y)
        random_data_mean = mean(y)
        anomaly_cut_off = random_data_std * 3

        lower_limit = random_data_mean - anomaly_cut_off
        upper_limit = random_data_mean + anomaly_cut_off
        # logging.info("Lower Limit {}, Upper Limit {}".format(lower_limit, upper_limit))
        # Generate outliers
        outlier_index = 0
        for outlier in y:
            if outlier > upper_limit or outlier < lower_limit:
                anomalies.append((outlier_index, outlier))
            outlier_index += 1

        outliers = pd.DataFrame.from_records(
            anomalies,
            columns=["Index", "Value"]
        )
        self.__df.drop(outliers["Index"])

    def create_models(self):
        y = self.__df.pop(self.__y_column_name)

        pipe = Pipeline(
            steps=[
                ("selection", SelectPercentile(percentile=10)),
                ("std_slc", StandardScaler()),
                ("estimator", LinearRegression())]
        )
        parameters = [
            #{"selection__score_func": [f_regression, mutual_info_regression]},
            # {
            #     "estimator": [DecisionTreeRegressor()],
            #     "estimator__max_depth": [1, 5, 9, 12, 14, 16],
            #     "estimator__min_samples_leaf": [1, 3, 5, 7, 9],
            # },
            {
                "estimator": [Lasso()],
                "estimator__alpha": np.arange(0, 1, 0.1)
            },
            {
                "estimator": [Ridge()],
                "estimator__alpha": np.arange(0, 1, 0.1)
            }]

        start_time = datetime.now()
        clf_GS = GridSearchCV(
            pipe,
            parameters,
            verbose=2,
            scoring=["r2", "neg_mean_squared_error",
                     "neg_root_mean_squared_error"],
            #n_jobs=int(SLURM_CPUS_PER_TASK),
            refit="r2"
        )
        end_time = datetime.now()
        delta = end_time - start_time
        logging.info(
            "gridsearch constructor call duration in minutes: {}".format(
                delta.seconds / 60
            )
        )

        start_time = datetime.now()
        with parallel_backend('threading', n_jobs=NUM_OF_JOBS):
            clf_GS.fit(self.__df, y)
        end_time = datetime.now()
        delta = end_time - start_time
        logging.info(
            "gridsearch fit call duration in minutes: {}".format(
                delta.seconds / 60
            )
        )
        logging.info("best_parameter: {}".format(clf_GS.best_params_))
        logging.info("best_score: {}".format(clf_GS.best_score_))
        df = pd.DataFrame.from_records(clf_GS.cv_results_)
        df.to_excel("cv_results.xlsx")
        featurelist = list(self.__df.columns.values)
        skb_step = clf_GS.best_estimator_.named_steps["selection"]
        feature_scores = ['%.2f' % elem for elem in skb_step.scores_ ]

        # Get SelectKBest pvalues, rounded to 3 decimal places, name them "feature_scores_pvalues"

        feature_scores_pvalues = ['%.3f' % elem for elem in  skb_step.pvalues_
                                  ]

        # Get SelectKBest feature names, whose indices are stored in 'skb_step.get_support',

        # create a tuple of feature names, scores and pvalues, name it "features_selected_tuple"

        features_selected_tuple=[(featurelist[i+1], feature_scores[i],
                                  feature_scores_pvalues[i]) for i in skb_step.get_support(indices=True)]

        # Sort the tuple by score, in reverse order

        features_selected_tuple = sorted(features_selected_tuple, key=lambda
                feature: float(feature[1]) , reverse=True)

        # Print

        logging.info(' ')
        logging.info('Selected Features, Scores, P-Values')
        logging.info(features_selected_tuple)

    def save_cmd_names_mapping(self):
        logging.info("save cmd names mapping")
        today = datetime.now().strftime("%Y-%m-%d")
        mapping_name = "cmd_names_mapping_{}.json".format(today)
        path_to_mapping_file = Path(self.__export_path) / mapping_name
        with open(path_to_mapping_file, "w") as file:
            json.dump(self.__db.get_cmd_int_dict(), file)

    def save_model(self, mae, mse, r_2_score, model, name):
        today = datetime.now().strftime("%Y-%m-%d")
        log_file_name = "{}_statistics_{}.txt".format(name, today)
        dump_file_name = "{}_model_{}.joblib".format(name, today)
        path_to_dump_file = Path(self.__export_path) / dump_file_name
        path_to_log_file = Path(self.__export_path) / log_file_name
        logging.info("dump file {}".format(path_to_dump_file))
        dump(model, path_to_dump_file)
        log_file = open(path_to_log_file, "w")
        log_file.write(
            "{name}: Accuracy: mae {mae:.3f} mse {mse:.2f} r2 score {r_2_score:.2%})".format(
                name=name, mae=mae,
                mse=mse, r_2_score=r_2_score
            )
        )
        column_names = ", ".join(self.__df.columns.values)
        log_file.write("\ndataframe columns: {}".format(column_names))
        log_file.close()


def main(config_file_path: str = "resources/config/analysis_config.json"):
    config_handler = AnalysisConfigurationHandler(config_file_path)
    config_handler.load_config()
    database = Database(config_handler)

    regression_analysis = RegressionAnalysis(config_handler, database)
    regression_analysis.start()


if __name__ == "__main__":
    typer.run(main)
