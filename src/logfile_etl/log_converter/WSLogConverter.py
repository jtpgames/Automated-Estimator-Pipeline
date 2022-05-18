import logging
import re
from os import SEEK_SET
from pathlib import Path
from src.logfile_etl.log_converter.AbstractLogFileConverter import (
    AbstractLogFileConverter,
)
from src.logfile_etl.TimeUtils import get_date_from_string


def peek_line(f):
    line = f.readline()
    count = len(line) + 1
    f.seek(f.tell() - count, SEEK_SET)
    return line


class WSLogConverter(AbstractLogFileConverter):
    def __init__(self):
        super().__init__()

    def does_applies_for_file(self, filename) -> bool:
        first_match = re.search("Worker-cmd", filename)
        second_match = re.search("WSCmd", filename)
        evaluation = first_match is not None or second_match is not None
        return evaluation

    def convert_log_file(
        self, filename, file_path: Path, writing_directory: Path
    ) -> bool:
        if "Worker-cmd" not in filename and "WSCmd" not in filename:
            logging.info("Either WSCmd or Worker-cmd should be part of the filename")
            return False

        new_logfile_name = "WSCmd_f_" + get_date_from_string(filename) + ".log"
        target_path = writing_directory / new_logfile_name

        logging.info("WSLogConverter converting {}".format(file_path))
        with open(file_path, encoding="latin-1") as logfile:
            with open(target_path, mode="w", encoding="latin-1") as targetFile:
                counter = 0

                first_line = logfile.readline()
                while first_line:
                    second_line = peek_line(logfile)

                    counter = counter + 1
                    if counter % 10000 == 0:
                        logging.info("Processed {} entries".format(counter))

                    if first_line.startswith("[") and second_line.startswith("["):
                        targetFile.write(first_line)
                    else:
                        targetFile.write(
                            "{}{}\n".format(
                                first_line.rstrip("\n"), second_line.strip()
                            )
                        )
                        logfile.readline()  # consume second line

                    first_line = logfile.readline()

        return True

    def __str__(self):
        return "WSLogConverter"
