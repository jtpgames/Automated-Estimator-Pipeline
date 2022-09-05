import json
import logging
import os
from dask.distributed import Client
import joblib
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
import typer
from joblib import dump, Parallel
# explicitly require this experimental feature
from sklearn.experimental import enable_halving_search_cv  # noqa
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline

from feature_extractor.cmd_extractor import CMDAnalysisExtractor
from src.database import Database
from src.configuration_handler import AnalysisConfigurationHandler
import time

from src.feature_extractor.feature_extractor_init import \
    get_feature_extractors_by_name_analysis


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)
handler = logging.StreamHandler(sys.stdout)


class RegressionAnalysis:
    __std_threshold = 3
    __df: pd.DataFrame
    __db: Database
    __grid_search_params: dict
    __config_handler: AnalysisConfigurationHandler

    def __init__(
            self,
            config_handler: AnalysisConfigurationHandler,
            db: Database
    ):
        self.__feature_extractors = None
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
            self.__config_handler.get_feature_extractor_names()
        )

    def load_data(self):
        for extractor in self.__feature_extractors:
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
        params = self.__config_handler.get_estimator_handler().get_params()
        steps = params["steps"]
        estimator_params = params["parameter_grid"]
        gs_params = params["grid_search_params"]
        pipe = Pipeline(steps)
        grid_search = GridSearchCV(pipe, estimator_params, **gs_params)
        client = Client(processes=False)  # create local cluster
        start = time.time()
        with joblib.parallel_backend('dask'):
            grid_search.fit(self.__df, y)
        end = time.time()
        logging.info("Exexution time for fit in min: {}".format(end - start))
        self.__save_results(grid_search)

    def __is_outlier(self, s):
        lower_limit = s.mean() - (s.std() * 3)
        upper_limit = s.mean() + (s.std() * 3)
        return ~s.between(lower_limit, upper_limit)

    # TODO vernünftig machen
    def __remove_outliers(self):
        if self.__config_handler.get_outlier_detection_type():
            delete_cmd_after = False
            if "cmd" not in self.__df.columns.values:
                extractor = CMDAnalysisExtractor(self.__db, "cmd")
                new_df = extractor.get_df()
                self.__df = pd.merge(
                    self.__df,
                    new_df,
                    how="inner",
                    left_index=True,
                    right_index=True
                )
                delete_cmd_after = True
                print(self.__df.info())
            self.__df = self.__df[~self.__df.groupby("cmd")[self.__config_handler.get_y_column_name()].apply(self.__is_outlier)]
            if delete_cmd_after:
                print(self.__df.info())
                self.__df.drop("cmd", axis=1)
        else:
            self.__df = self.__df[
                np.abs(
                    self.__df[self.__config_handler.get_y_column_name()] - self.__df[
                        self.__config_handler.get_y_column_name()].mean()
                ) <= (
                        self.__std_threshold * self.__df[
                    self.__config_handler.get_y_column_name()].std())]


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
        estimators_string = " ".join([str(elem) for elem in self.__config_handler.get_estimator_handler().estimators])
        log_file.write("\ndataframe columns: {}".format(column_names))
        log_file.write("\ndatabase limit: {}".format(self.__config_handler.get_db_limit()))
        log_file.write("\nbest_parameter: {}".format(grid_search.best_params_))
        log_file.write("\npipeline: {}".format(self.__config_handler.get_estimator_handler().pipelines))
        log_file.write("\nestimators: {}".format(estimators_string))
        log_file.close()

    def __get_scores_from_cv_result(self, cv_results):
        # TODO rename
        params = self.__config_handler.get_estimator_handler().get_grid_search_parameter()
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
        # if self.__config_handler.use_feature_selection():
        #     featurelist = list(self.__df.columns.values)
        #     skb_step = grid_search.best_estimator_.named_steps["feature_selection"]
        #     feature_scores = ['%.2f' % elem for elem in skb_step.scores_]
        #     feature_scores_pvalues = ['%.3f' % elem for elem in skb_step.pvalues_]
        #     features_selected_tuple = [(featurelist[i + 1], feature_scores[i],
        #                                 feature_scores_pvalues[i]) for i in
        #                                skb_step.get_support(indices=True)]
        #     features_selected_tuple = sorted(
        #         features_selected_tuple, key=lambda
        #             feature: float(feature[1]), reverse=True
        #     )
        #     logging.info(' ')
        #     logging.info('Selected Features, Scores, P-Values')
        #     logging.info(features_selected_tuple)


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
