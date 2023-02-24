import logging

from src.analysis.data_preparatio import DataPreparation
from src.analysis.grid_search_wrapper import GridSearchWrapper
from src.analysis.outlier_detection import OutlierDetection
from src.configuration import Configuration
from src.database import Database


class EstimatorPipeline:
    __outlier_detection: OutlierDetection
    __data_preparation: DataPreparation
    __grid_search: GridSearchWrapper

    def __init__(self, config: Configuration):
        db = Database(config.for_database())
        self.__data_preparation = DataPreparation(config.for_estimator_pipeline(), db)
        self.__outlier_detection = OutlierDetection(config.for_outlier_detection(), db)
        self.__grid_search = GridSearchWrapper(config.for_estimator_pipeline().grid_search_wrapper, db,
                                               config.get_config())

    def run(self):
        logging.info("start estimator pipeline")
        logging.info("getting data")
        X, y = self.__data_preparation.get_dataset()
        logging.info("removing outliers")
        X, y = self.__outlier_detection.remove_outliers(X, y)
        logging.info("start fitting estimators")
        self.__grid_search.setup()
        self.__grid_search.fit(X, y)
        self.__grid_search.save_results()
