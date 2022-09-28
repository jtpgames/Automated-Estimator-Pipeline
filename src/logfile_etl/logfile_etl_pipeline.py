from factory.factories import LogfileFeatureExtractorFactory
from src.configuration import Configuration
from src.database import Database
from src.logfile_etl.log_converter.logfile_converter import LogfileConverter
from src.logfile_etl.logfile_merger import LogMerger
from src.logfile_etl.merged_logfile_processor import MergedLogProcessor


class LogfileETLPipeline:
    __config_handler: Configuration
    __database: Database
    __skip_stages: dict[str, bool]

    def __init__(self, config_handler: Configuration, database: Database, skip_stages: dict[str, bool]):
        self.__config_handler = config_handler
        self.__database = database
        self.__skip_stages = skip_stages

    def run(self):
        if not self.__skip_stages["converter"]:
            converter = LogfileConverter(self.__config_handler)
            converter.convert_logfiles()
        if not self.__skip_stages["merger"]:
            merger = LogMerger(self.__config_handler)
            merger.merge_logfiles()

        extractors = self.__initialize_feature_extractors()
        processor = MergedLogProcessor(self.__config_handler, self.__database, extractors)
        processor.process_merged_logs()
        processor.save_features_to_db()

    def __initialize_feature_extractors(self):
        extractors = []
        factory = LogfileFeatureExtractorFactory()
        for name in self.__config_handler.get_logfile_feature_extractor_names():
            extractor_class = factory.get(name)
            # initialize extractor class with his name as constructor argument
            extractor_object = extractor_class(name)
            extractors.append(extractor_object)
        return extractors
