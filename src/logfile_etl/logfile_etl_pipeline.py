from src.dto.dtos import LogfileETLPipelineDTO
from src.factory.factories import LogfileFeatureExtractorFactory
from src.configuration import Configuration
from src.database import Database
from src.logfile_etl.log_converter.logfile_converter import LogfileConverter
from src.logfile_etl.logfile_merger import LogMerger
from src.logfile_etl.merged_logfile_processor import MergedLogProcessor


class LogfileETLPipeline:
    __config: LogfileETLPipelineDTO
    __database: Database
    __skip_stages: dict[str, bool]

    def __init__(self, config: Configuration, skip_stages: dict[str, bool]):
        self.__config = config.for_logfile_etl()
        self.__database = Database(config.for_database())
        self.__skip_stages = skip_stages

    def run(self):
        if not self.__skip_stages["converter"]:
            converter = LogfileConverter(self.__config)
            converter.convert_logfiles()
        if not self.__skip_stages["merger"]:
            merger = LogMerger(self.__config)
            merger.merge_logfiles()

        extractors = self.__initialize_feature_extractors()
        processor = MergedLogProcessor(self.__config, self.__database, extractors)
        processor.process_merged_logs()
        processor.save_features_to_db()

    def __initialize_feature_extractors(self):
        extractors = []
        factory = LogfileFeatureExtractorFactory()
        for name in self.__config.extractors:
            extractor_class = factory.get(name)
            # initialize extractor class with his name as constructor argument
            extractor_object = extractor_class(name)
            extractors.append(extractor_object)
        return extractors
