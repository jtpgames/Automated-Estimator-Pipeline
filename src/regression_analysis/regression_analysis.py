import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Any

import typer
import pandas as pd
from joblib import dump, load
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV

from sklearn import decomposition, datasets, tree
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.regression_analysis.configuration_handler import ConfigurationHandler
from src.regression_analysis.database import Database
from src.regression_analysis.features.abstract_feature_extractor import (
    AbstractFeatureExtractor,
)
from src.regression_analysis.features.feature_extractors import (
    get_feature_extractors_by_name,
)
from numpy import std, mean

from src.regression_analysis.models.models import get_model_objects_from_names

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)


class RegressionAnalysis:
    __db_path: str
    __cmd_numbers_mapping = {}
    __df: pd.DataFrame
    __features_extractors: List[AbstractFeatureExtractor] = []
    __models: List[tuple[str, Any]]
    __db: Database
    __y_column_name: str

    def __init__(self, config_handler: ConfigurationHandler):
        self.__models = get_model_objects_from_names(
            config_handler.get_models()
        )
        self.__db = Database(config_handler)
        self.__df = pd.DataFrame()
        self.__features_extractors = get_feature_extractors_by_name(
            config_handler.get_features()
        )
        self.__y_column_name = config_handler.get_y_column_name()
        self.__export_path = config_handler.get_model_save_path()

    def load_data(self):
        logging.info(
            "number feature extractors: {}".format(
                len(self.__features_extractors)
            )
        )
        for extractor in self.__features_extractors:
            logging.info(
                "Loading values of extractor: {}".format(
                    extractor.get_column_name()
                )
            )
            if self.__df.empty:
                self.__df = extractor.get_df(
                    self.__db,
                    self.__cmd_numbers_mapping
                )
            else:
                new_df = extractor.get_df(self.__db, self.__cmd_numbers_mapping)
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
        logging.info("-------")
        logging.info("unscaled")
        logging.info(self.__df)

        std_slc = StandardScaler()
        pcd = decomposition.PCA()
        dec_tree = tree.DecisionTreeClassifier()
        pipe = Pipeline(steps)[('std_cla', std_cla), ('pca', pca),('dec_tree', dec_tree)]

        n_components = list(range(1,X.shape[1]+1,1))
        criterion = ['gini', 'entropy']
        max_depth = [2,4,6,8,10,12]

        parameters = dict(pca__n_components=n_components,dec_tree__criterion=criterion, dec_tree__max_depth=max_depth)
        clf_GS = GridSearchCV(pipe, parameters)

        x_train, x_test, y_train, y_test = train_test_split(
            self.__df, y, test_size=0.2, random_state=42
        )
        clf_GS.fit(x_train, y_train)

        print('Best Criterion:', clf_GS.best_estimator_.get_params()['dec_tree__criterion'])
        print('Best max_depth:', clf_GS.best_estimator_.get_params()['dec_tree__max_depth'])
        print('Best Number Of Components:', clf_GS.best_estimator_.get_params()['pca__n_components'])
        print(); print(clf_GS.best_estimator_.get_params()['dec_tree'])

        clf_GS.score(x_test, y_test)
        # y = self.__df.pop(self.__y_column_name)
        # logging.info("-------")
        # logging.info("unscaled")
        # logging.info(self.__df)
        # # x_scaled = StandardScaler().fit_transform(self.__df)
        # # logging.info("scaled")
        # # logging.info(x_scaled.mean(axis=0))
        # # logging.info(x_scaled.std(axis=0))

        # x_train, x_test, y_train, y_test = train_test_split(
        #     self.__df, y, test_size=0.2, random_state=42
        # )

        # logging.info("====")
        # logging.info("== Evaluating each model in turn ==")
        # results = []
        # names = []
        # for name, model in self.__models:
        #     # cv_results = cross_val_score(model, x_train, y_train)
        #     model.fit(x_train, y_train)
        #     # results.append(cv_results)
        #     # names.append(name)
        #     # logging.info(
        #     #     "%s: Accuracy: %0.2f (+/- %0.2f)"
        #     #     % (name, cv_results.mean(), cv_results.std() * 2)
        #     # )

        #     logging.info("== X_test ==")
        #     logging.info(x_test)
        #     logging.info("== Predictions ==")
        #     predictions = model.predict(x_test)
        #     logging.info(predictions)
        #     logging.info("== y_test ==")
        #     logging.info(y_test)
        #     logging.info("====")

        #     # The coefficients
        #     # logging.info("Model Coefficients: ", model.coef_)
        #     # logging.info("Model intercept: ", model.intercept_)
        #     mae = mean_absolute_error(y_test, predictions)
        #     mse = mean_squared_error(y_test, predictions)
        #     r_2_score = r2_score(y_test, predictions)
        #     logging.info(
        #         'Mean absolute error: {:.3f}'.format(mae)
        #     )
        #     # The mean squared error
        #     logging.info(
        #         'Mean squared error: {:.2f}'.format(mse)
        #     )

        #     # The coefficient of determination: 1 is perfect prediction
        #     logging.info(
        #         'Coefficient of determination: {:.2%}'.format(r_2_score)
        #     )
        #     self.save_model(mae, mse, r_2_score, model, name)

        # self.save_cmd_names_mapping()
        # logging.info("====")

        # # for model in self.__models:
        # #     model.fit()

    def save_cmd_names_mapping(self):
        logging.info("save cmd names mapping")
        today = datetime.now().strftime("%Y-%m-%d")
        mapping_name = "cmd_names_mapping_{}.json".format(today)
        path_to_mapping_file = Path(self.__export_path) / mapping_name
        with open(path_to_mapping_file, "w") as file:
            json.dump(self.__cmd_numbers_mapping, file)

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
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    regression_analysis = RegressionAnalysis(config_handler)
    regression_analysis.load_data()
    regression_analysis.create_models()


if __name__ == "__main__":
    typer.run(main)
