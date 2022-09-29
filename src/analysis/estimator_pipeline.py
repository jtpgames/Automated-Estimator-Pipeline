from analysis.data_preparatio import DataPreparation
from analysis.grid_search_wrapper import GridSearchWrapper
from analysis.outlier_detection import OutlierDetection
from configuration import Configuration
from src.database import Database


class EstimatorPipeline:
    __db: Database
    __config_handler: Configuration

    def __init__(self, config_handler: Configuration, db: Database):
        self.__config_handler = config_handler
        self.__db = db

    def run(self):
        data_preparation = DataPreparation(self.__config_handler.get_feature_extractor_names(), self.__db)
        df = data_preparation.get_feature_df()

        outlier_detection = OutlierDetection(self.__config_handler, self.__db)
        df = outlier_detection.remove_outliers_inplace(df)
        
        grid_search = GridSearchWrapper(self.__config_handler, self.__db)
        grid_search.setup()
        y = df.pop(self.__config_handler.get_y_column_name())
        grid_search.fit(df, y)
        grid_search.save_results()
