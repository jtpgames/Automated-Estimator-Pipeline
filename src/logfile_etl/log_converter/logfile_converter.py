import logging
import shutil
from pathlib import Path

from dto.dtos import LogfileETLPipelineDTO
from factory.factories import ConverterFactory
from logfile_etl.log_converter.abstract_logfile_converter import AbstractLogfileConverter


class LogfileConverter:
    __converters: list[AbstractLogfileConverter]

    def __init__(self, config: LogfileETLPipelineDTO):
        factory = ConverterFactory()
        self.__converters = [factory.get(x)() for x in config.converter]
        self.__input_dir_path = Path(config.unprocessed_logfiles_folder)
        self.__output_dir_path = Path(config.processed_logfiles_folder)
        self.__create_dirs_if_necessary()

    def convert_logfiles(self):
        logging.info("Start converting logfiles")
        logging.info("registered converter: {}".format(self.__converters))
        files = self.load_files_in_input_dir()
        converted_files = []

        for file in files:
            for converter in self.__converters:
                if converter.does_applies_for_file(file.name):
                    converter.convert_log_file(
                        file.name, self.__input_dir_path / file, self.__output_dir_path
                    )
                    converted_files.append(file)

        files_matching_no_converter = [
            file for file in files if file not in converted_files
        ]
        logging.info("Files without explicit converter: {}".format(files_matching_no_converter))
        self.copy_files_with_no_matching_converter(files_matching_no_converter)

    def copy_files_with_no_matching_converter(self, unconverted_files):
        logging.info("Copying remaining files to processed directory")
        file_counter = 0
        for file in unconverted_files:
            input_path = self.__input_dir_path / file.name
            output_path = self.__output_dir_path / file.name
            shutil.copyfile(input_path, output_path)
            logging.info(
                "File {} of {} copied".format(file_counter, len(unconverted_files))
            )

    def load_files_in_input_dir(self):
        p = self.__input_dir_path.glob("**/*")
        files = [x for x in p if x.is_file()]
        return files

    def __create_dirs_if_necessary(self):
        Path(self.__input_dir_path).mkdir(parents=True, exist_ok=True)
        Path(self.__output_dir_path).mkdir(parents=True, exist_ok=True)
