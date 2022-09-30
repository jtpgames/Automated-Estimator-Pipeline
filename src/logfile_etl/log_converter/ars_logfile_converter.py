import logging
import re

from src.logfile_etl.log_converter.abstract_logfile_converter import (
    AbstractLogfileConverter,
)


class ARSLogConverter(AbstractLogfileConverter):
    def does_applies_for_file(self, filename) -> bool:
        match = re.search("Koppel-cmd", filename)
        return match is not None

    def convert_log_file(self, filename, file_path, writing_directory) -> bool:
        if "Koppel-cmd" not in filename:
            logging.info("Koppel-cmd should be part of the filename")
            return False

        target_filename = filename.replace("Koppel-cmd", "ARS")
        target_path = writing_directory / target_filename

        logging.info("ARSLogConverter converting {}".format(file_path))
        with open(file_path, encoding="latin-1") as logfile:
            with open(target_path, mode="w") as targetFile:
                counter = 0

                for line in logfile:
                    counter = counter + 1
                    if counter % 10000 == 0:
                        logging.info("Processed {} entries".format(counter))

                    targetFile.write("{}\n".format(line.strip()))

        return True

    def __str__(self):
        return "ARSLogConverter"
