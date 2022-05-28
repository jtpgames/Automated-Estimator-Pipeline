import logging

import typer

from src.logfile_etl.log_converter.logfile_converter import LogfileConverter
from src.logfile_etl.logfile_merger import LogMerger
from src.logfile_etl.merged_logfile_processor import MergedLogProcessor
from src.logfile_etl.configuration_handler import ConfigurationHandler

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO
)

app = typer.Typer()


@app.command()
def convert_logs(config_file_path: str = "resources/config/etl_config.json"):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    log_converter = LogfileConverter(config_handler)
    log_converter.convert_logfiles()


@app.command()
def merge_logs(config_file_path: str = "resources/config/etl_config.json"):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    log_merger = LogMerger(config_handler)
    log_merger.merge_logfiles()


@app.command()
def extract_features(
        config_file_path: str = "resources/config/etl_config.json"
):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    feature_extractor = MergedLogProcessor(config_handler)
    feature_extractor.process_merged_logs()
    feature_extractor.save_features_to_db()


@app.callback(invoke_without_command=True)
def run_etl_process(config_file_path: str = "resources/config/etl_config.json"):
    config_handler = ConfigurationHandler(config_file_path)
    config_handler.load_config()

    log_converter = LogfileConverter(config_handler)
    log_converter.convert_logfiles()
    log_merger = LogMerger(config_handler)
    log_merger.merge_logfiles()

    feature_extractor = MergedLogProcessor(config_handler)
    feature_extractor.process_merged_logs()
    feature_extractor.save_features_to_db()


if __name__ == "__main__":
    app()
