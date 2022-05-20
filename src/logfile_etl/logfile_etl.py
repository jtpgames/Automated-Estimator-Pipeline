import logging

import typer

from src.logfile_etl.log_converter.logfile_converter import LogfileConverter
from src.logfile_etl.logfile_merger import LogMerger
from src.logfile_etl.merged_logfile_processor import MergedLogProcessor
from src.logfile_etl.configuration_handler import ConfigurationHandler

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def main(config_file_path: str = "resources/config/etl_config.json"):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    # TODO cli for single action use cases
    log_converter = LogfileConverter(config_handler)
    log_converter.convert_logfiles()
    log_merger = LogMerger(config_handler)
    log_merger.merge_logfiles()

    feature_extractor = MergedLogProcessor(config_handler)
    feature_extractor.process_merged_logs()
    feature_extractor.save_features_to_db()


if __name__ == "__main__":
    typer.run(main)
