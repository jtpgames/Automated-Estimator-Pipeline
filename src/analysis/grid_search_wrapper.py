import json
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from joblib import dump
from sklearn.feature_selection import f_regression, mutual_info_regression, SelectPercentile
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.pipeline import Pipeline

from database import Database
from dto.dtos import GridSearchDTO, CrossValidationDTO, GridSearchWrapperDTO
from factory.factories import EstimatorFactory, EstimatorPipelineActionFactory


# TODO Cleanup

score_funcs = [f_regression, mutual_info_regression, SelectPercentile]

class GridSearchWrapper:
    __column_names = None
    __grid_search = None
    __parameter_grid = None
    __config_json: any
    __config = GridSearchWrapperDTO
    __db = Database
    __estimator_factory = EstimatorFactory()
    __action_factory = EstimatorPipelineActionFactory()

    def __init__(self, config: GridSearchWrapperDTO, database: Database, config_json: any):
        self.__config_json = config_json
        self.__config = config
        self.__db = database

    def setup(self):
        self.__set_all_gs_params()
        gs_params = GridSearchDTO.Schema().dump(self.__config.grid_search)
        cv_params = CrossValidationDTO.Schema().dump(self.__config.cross_validation)
        pipe = Pipeline(self.__all_pipeline_steps)
        cv = KFold(**cv_params)
        self.__grid_search = GridSearchCV(pipe, self.__parameter_grid, **gs_params, cv=cv)

    def __set_all_gs_params(self):
        all_step_names = []
        self.__parameter_grid = []
        self.__set_pipeline_for_estimators()
        for estimator_config in self.__config.estimators:
            estimator = self.__estimator_factory.get(estimator_config.name)()
            params_to_rename = estimator_config.params
            params = {"estimator": [estimator]}

            for pipeline in self.__config.pipelines:
                if estimator_config.name in pipeline.for_estimators:
                    for step in pipeline.steps:
                        # pipeline step name with prefix for compatible estimators e.g. dt_linear_scaler
                        step_prefix = "_".join(pipeline.for_estimators) + "_"
                        step_name = step_prefix + step.step
                        # add step name to all pipeline steps list if not already present
                        if step_name not in all_step_names:
                            all_step_names.append(step_name)
                        # initalize action with estimator as input if needed and add
                        # to the parameter grid of the estimator. e.g. dt_select_from_model: [SelectFromModel(estimator)]
                        action = self.__action_factory.get(step.action)
                        if step.needs_estimator:
                            params[step_name] = [action(estimator)]
                        else:
                            params[step_name] = [action()]
                        # add all remaining grid params with pipeline
                        for key, value in step.params.items():
                            if isinstance(value, list):
                                arr = []
                                for x in value:
                                    arr.append(self.__eval_str_value_else_return(x))
                                params[step_name + "__" + key] = arr
                            else:
                                params[step_name + "__" + key] = self.__eval_str_value_else_return(value)



            for key, value in params_to_rename.items():
                params["estimator__" + key] = value

            self.__parameter_grid.append(params)

        # add estimator as last pipeline step
        all_step_names.append("estimator")
        # all pipeline steps
        self.__all_pipeline_steps = []
        for step in all_step_names:
            self.__all_pipeline_steps.append((step, "passthrough"))

    @staticmethod
    def __eval_str_value_else_return(x):
        if isinstance(x, str):
            return eval(x)
        else:
            return x


    def fit(self, X, y):
        self.__column_names = ", ".join([str(x) for x in X.columns.values])
        self.__grid_search.fit(X, y)

    def __set_pipeline_for_estimators(self):
        if len(self.__config.pipelines) == 1:
            self.__config.pipelines[0].for_estimators = [estimator.name for estimator in
                                                         self.__config.estimators]

    def __get_grid_search_parameter(self):
        # if multiple scoring metrices are defined, refit has to be set
        if self.__config.grid_search.refit is not None:
            return {
                "key": "rank_test_" + self.__config.grid_search.refit,
                "values": ["mean_test_" + x for x in self.__config.grid_search.scoring],
                "names": self.__config.grid_search.scoring
            }
        else:
            # if refit is not set, then scoring has to be a single value
            return {"key": "rank_test_score", "values": ["mean_test_score"],
                    "names": [self.__config.grid_search.scoring]}

    # def uses_feature_selector(self):
    #     pipeline_steps = [step.step for pipeline in self.__estimator_handler.pipelines for step in pipeline.steps]
    #     print("feature_selection" in pipeline_steps)
    #     return "feature_selection" in pipeline_steps

    def save_results(self):
        self.__log_results(self.__grid_search)

        path_to_folder = self.__create_folder_for_estimator_saving(self.__grid_search)

        self.__save_estimator(self.__grid_search, path_to_folder)
        self.__save_cmd_names_mapping(path_to_folder)
        self.__save_cv_results(self.__grid_search, path_to_folder)
        self.__save_config(path_to_folder)

    def __create_folder_for_estimator_saving(self, grid_search):
        today = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        estimator_name = grid_search.best_estimator_.named_steps["estimator"].__class__.__name__
        scores = self.__get_scores_from_cv_result(grid_search.cv_results_)
        folder_name = "{}_{}_{}_{:.2f}".format(today, estimator_name, scores[1][0], scores[0][0])
        path_to_folder = Path(
            self.__config.export_folder
        ) / folder_name
        os.makedirs(path_to_folder, exist_ok=True)
        return path_to_folder

    def __save_cv_results(self, grid_search, path_to_folder):
        df = pd.DataFrame.from_records(grid_search.cv_results_)
        logging.info("save cv results")
        mapping_name = "cv_results_100000.xlsx"
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
        estimators_string = " ".join([str(elem) for elem in self.__config.estimators])
        log_file.write("\ndataframe columns: {}".format(self.__column_names))
        log_file.write("\nbest_parameter: {}".format(grid_search.best_params_))
        log_file.write("\nestimators: {}".format(estimators_string))
        log_file.close()

    def __get_scores_from_cv_result(self, cv_results):
        params = self.__get_grid_search_parameter()
        df = pd.DataFrame.from_records(cv_results)
        scores = df[df[params["key"]] == 1][params["values"]].mean().values
        names = params["names"]
        return scores, names

    def __save_cmd_names_mapping(self, path_to_folder):
        logging.info("save cmd names mapping")
        mapping_name = "cmd_names_mapping.json"
        path_to_mapping_file = Path(path_to_folder) / mapping_name
        with open(path_to_mapping_file, "w") as file:
            json.dump(self.__db.get_cmd_mapping(cmd_key=True), file)

    def __save_estimator(self, grid_search, path_to_folder):
        estimator_name = grid_search.best_estimator_.named_steps["estimator"].__class__.__name__
        dump_file_name = "{}_model.joblib".format(estimator_name)
        path_to_dump_file = Path(path_to_folder) / dump_file_name
        logging.info("dump file {}".format(path_to_dump_file))
        dump(grid_search.best_estimator_, path_to_dump_file)

    # get_feature_names_out(input_features=None)[source]
    def __log_results(self, grid_search):
        logging.info("best_parameter: {}".format(grid_search.best_params_))
        logging.info("best_score: {}".format(grid_search.best_score_))
        # if self.__config_handler.use_feature_selection():
        #     featurelist = list(self.__df.columns.values)
        #     skb_step = grid_search.best_estimator_.named_steps["Ridge_feature_selection"]
        #     print(skb_step)
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

    def __save_config(self, path_to_folder):
        conf = self.__config_json
        file = Path(path_to_folder) / "config.json"
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(conf, f, ensure_ascii=False, indent=4)
