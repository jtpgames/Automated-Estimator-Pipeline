import glob
import logging
from datetime import datetime
from os.path import join
from re import search
from typing import List, Tuple

from dto.dtos import LogfileETLPipelineDTO
from src.database import Database
from src.feature_extractor.abstract_feature_extractor import (
    AbstractETLFeatureExtractor,
)
from src.logfile_etl.parallel_commands_tracker import ParallelCommandsTracker
from src.utils import get_timestamp_from_string, contains_timestamp_with_ms


class MergedLogProcessor:
    __feature_extractors: List[AbstractETLFeatureExtractor] = []
    __data = {}
    __data_arr = []
    __parallel_commands_tracker = ParallelCommandsTracker()
    __reading_directory: str
    __db: Database
    __force: bool

    def __init__(self, config: LogfileETLPipelineDTO, database: Database,
                 feature_extractors: List[AbstractETLFeatureExtractor]):
        self.__force = config.force
        self.__reading_directory = config.processed_logfiles_folder
        self.__feature_extractors = feature_extractors
        self.__db = database
        self.__initialize_data()

    def process_merged_logs(self):
        logging.info("Start extracting features of merged logfiles")

        logging.info("Extractors: {}".format(self.__feature_extractors))
        logfiles_to_convert = glob.glob(
            join(self.__reading_directory, "Merged_*.log")
        )

        # remove duplicates trick
        logfiles_to_convert = sorted(set(logfiles_to_convert))

        logging.info("Logs to process: {}".format(str(logfiles_to_convert)))
        for path in logfiles_to_convert:
            logging.info("processing {}".format(path))
            self.__extract_features(path)

    def __initialize_data(self):
        for extractor in self.__feature_extractors:
            self.__data[extractor.get_feature_name()] = []

    def __extract_features(self, path):
        with open(path, encoding="latin-1") as logfile:
            entry_counter = 0
            for line in logfile:
                entry_counter = entry_counter + 1
                if entry_counter % 20000 == 0:
                    logging.info("Processed {} entries".format(entry_counter))
                tid, timestamp = MergedLogProcessor.__get_thread_id_and_timestamp(
                    line
                )
                if "CMD-START" in line:
                    self.__process_start_line(line, tid, timestamp)
                if "CMD-END" in line:
                    self.__process_end_line(line, tid, timestamp, logfile)

        self.__handle_remaining_commands()
        self.__cleanup()

    def __process_start_line(self, line, tid, timestamp):
        if tid in self.__parallel_commands_tracker:
            logging.info(
                tid,
                " already processes another command",
                self.__parallel_commands_tracker[tid]["cmd"],
            )
            logging.info("new line ", line)
            if not self.__force:
                input("Press ENTER to continue...")
            return

        self.__parallel_commands_tracker.add_command(
            tid, timestamp, self.__extract_command_name(line)
        )

    def __process_end_line(self, line, tid, timestamp, logfile):

        if tid not in self.__parallel_commands_tracker:
            logging.info("Command ended without corresponding start log entry")
            logging.info("in file: {}".format(logfile))
            logging.info("on line: {}".format(line))
            logging.info(self.__parallel_commands_tracker)
            if not self.__force:
                input("Press ENTER to continue...")
            return
        # prepare command for feature extraction and deletion from parallel_commands_tracker
        self.__parallel_commands_tracker[tid]["respondedAt"] = timestamp
        self.__parallel_commands_tracker[tid][
            "parallelCommandsEnd"
        ] = self.__parallel_commands_tracker.command_count(except_one=True)
        self.__parallel_commands_tracker[tid][
            "listParallelCommandsEnd"] = self.__parallel_commands_tracker.get_list_parallel_commands(tid)

        entry = {}
        for extractor in self.__feature_extractors:
            entry[extractor.get_feature_name()] = extractor.extract_feature(self.__parallel_commands_tracker, tid)
            # self.__data[extractor.get_feature_name()].append(
            #     extractor.extract_feature(self.__parallel_commands_tracker, tid)
            # )
        self.__data_arr.append(entry)
        self.__parallel_commands_tracker.remove_command(tid)

    def __handle_remaining_commands(self):
        if self.__parallel_commands_tracker.command_count() > 0:
            logging.info("Commands remaining")
            logging.info(self.__parallel_commands_tracker)
            if not self.__force:
                input("Press ENTER to continue...")

    def __cleanup(self):
        self.__parallel_commands_tracker.reset()

    def save_features_to_db(self):
        # self.__db.write(self.__data, self.__parallel_commands_tracker.get_command_mapping())
        feature_columns = [feature.get_column() for feature in self.__feature_extractors]
        self.__db.write_arr(feature_columns, self.__data_arr, self.__parallel_commands_tracker.get_command_mapping())

    @staticmethod
    def __extract_command_name(line: str):
        cmd = "ID_Unknown"
        if "unbekanntes CMD" not in line:
            cmd = search(r"ID_\w+", line).group()
        return cmd

    @staticmethod
    def __get_thread_id_and_timestamp(line: str) -> Tuple[int, datetime]:
        # format: [tid] yyyy-MM-dd hh-mm-ss.f

        tid = MergedLogProcessor.__get_thread_id_from_line_optimized(line)
        timestamp = MergedLogProcessor.__get_timestamp_from_line(line)
        return tid, timestamp

    @staticmethod
    def __get_timestamp_from_line(line: str) -> datetime:
        if contains_timestamp_with_ms(line):
            format_string = "%Y-%m-%d %H:%M:%S.%f"
        else:
            format_string = "%Y-%m-%d %H:%M:%S"

        return datetime.strptime(get_timestamp_from_string(line), format_string)

    @staticmethod
    def __get_thread_id_from_line_optimized(line: str) -> int:
        found_left_bracket = False
        tid_string = []

        for c in line:
            if c == "[":
                found_left_bracket = True
                continue
            elif c == "]":
                break

            if found_left_bracket:
                tid_string.append(c)

        tid_string = "".join(tid_string)
        tid = int(tid_string)

        return tid
