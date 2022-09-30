from analysis.data_preparatio import DataPreparation
from analysis.grid_search_wrapper import GridSearchWrapper
from analysis.outlier_detection import OutlierDetection
from configuration import Configuration
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
        X, y = self.__data_preparation.get_dataset()
        print("------------------------------------------")
        print("           before outlier removal         ")
        print("------------------------------------------")
        print(X.info())
        print(y)
        X, y = self.__outlier_detection.remove_outliers(X, y)

        print("------------------------------------------")
        print("            after outlier removal         ")
        print("------------------------------------------")
        print(X.info())
        print(y)
        self.__grid_search.setup()
        self.__grid_search.fit(X, y)
        self.__grid_search.save_results()
