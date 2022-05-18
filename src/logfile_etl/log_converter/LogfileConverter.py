import logging
import shutil

from src.logfile_etl.log_converter.WSLogConverter import WSLogConverter
from src.logfile_etl.log_converter.ARSLogConverter import ARSLogConverter
from src.logfile_etl.ConfigurationHandler import ConfigurationHandler


class LogfileConverter:
    __converters = [WSLogConverter(), ARSLogConverter()]

    def __init__(self, config_handler: ConfigurationHandler):
        self.input_dir = config_handler.get_unprocessed_logfile_dir()
        self.output_dir = config_handler.get_processed_logfile_dir()

    def convert_logfiles(self):
        logging.info("Start converting logfiles")
        logging.info("registered converter: {}".format(self.__converters))
        files = self.load_files_in_input_dir()
        converted_files = []

        for file in files:
            for converter in self.__converters:
                if converter.does_applies_for_file(file.name):
                    converter.convert_log_file(
                        file.name, self.input_dir / file, self.output_dir
                    )
                    converted_files.append(file)

        files_matching_no_converter = [
            file for file in files if file not in converted_files
        ]
        logging.info("Files without explicit converter: ", files_matching_no_converter)
        self.copy_files_with_no_matching_converter(files_matching_no_converter)

    def copy_files_with_no_matching_converter(self, unconverted_files):
        logging.info("Copying remaining files to processed directory")
        file_counter = 0
        for file in unconverted_files:
            input_path = self.input_dir / file.name
            output_path = self.output_dir / file.name
            # TODO create folder based on the creation date
            shutil.copyfile(input_path, output_path)
            logging.info(
                "File {} of {} copied".format(file_counter, len(unconverted_files))
            )

    def load_files_in_input_dir(self):
        p = self.input_dir.glob("**/*")
        files = [x for x in p if x.is_file()]
        return files
