import glob
import logging
from os.path import join

from itertools import groupby
from src.logfile_etl.TimeUtils import get_date_from_string, get_timestamp_from_string
from src.logfile_etl.ConfigurationHandler import ConfigurationHandler


class LogMerger:
    def __init__(self, config_handler: ConfigurationHandler):
        self.__reading_directory = config_handler.get_processed_logfile_dir()

    def merge_logfiles(self):
        logging.info(
            "Start merging converted logfiles in: {}".format(self.__reading_directory)
        )
        logfiles = glob.glob(join(self.__reading_directory, "*.log"))

        logging.info("Found logfiles: {}".format(logfiles))

        # group the files by the date in the file name
        data = sorted(logfiles, key=get_date_from_string)
        for group, logfile in groupby(data, key=get_date_from_string):
            # omit the merged logs created by this script
            logfile_to_aggregate = filter(lambda f: "Merged_" not in f, list(logfile))
            self.__aggregate(group, list(logfile_to_aggregate))

    def __aggregate(self, group: str, similar_logfile_paths: list):
        target_path = join(self.__reading_directory, "Merged_%s.log" % group)
        logging.info("Merging %s" % similar_logfile_paths)
        result_file = LogMerger.__merge(*similar_logfile_paths)
        logging.info("Merged %i log entries" % len(result_file))
        logging.info("Writing to ", target_path)
        with open(target_path, mode="w", encoding="latin-1") as targetFile:
            counter = 0
            for line in result_file:
                if counter % 20000 == 0:
                    logging.info("Written {} entries".format(counter))
                targetFile.write(line)
                counter += 1

    @staticmethod
    def __read_files(*filenames):
        counter = 0

        for filename in filenames:
            logging.info("Reading {}".format(filename))
            with open(filename, "r", encoding="latin-1") as file_obj:
                for line in file_obj:
                    counter = counter + 1
                    if counter % 20000 == 0:
                        logging.info("Processed {} entries".format(counter))

                    yield line

    @staticmethod
    def __merge(*seqs):
        return sorted(LogMerger.__read_files(*seqs), key=get_timestamp_from_string)
