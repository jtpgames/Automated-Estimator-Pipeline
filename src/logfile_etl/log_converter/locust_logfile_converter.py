import re

import uuid as uuid
from datetime import datetime, timedelta
from pathlib import Path
from random import randint

from src.logfile_etl.log_converter.abstract_logfile_converter import AbstractLogfileConverter

class LocustLogfileConverter(AbstractLogfileConverter):
    pattern = re.compile("\[([0-9- :,]*)\].*\[(SUCCESS|FAILURE)\]\[([a-zA-Z0-9-:,. \/=?&%]*)\]\[([\d.]*)\]")
    def does_applies_for_file(self, filename) -> bool:
        match = re.search("locust", filename)
        return match is not None

    def get_cmd(self, url: str) -> str:
        if url.find("loginAction?username") > -1:
            return "ID_login"
        if url.find("loginAction?logout") > -1:
            return "ID_logout"
        if url.find("cartAction?firstname") > -1:
            return "ID_order"
        if url.find("cartAction?addToCart") > -1:
            return "ID_add_to_cart"
        if url.find("category") > -1:
            return "ID_category"
        if url.find("product") > -1:
            return "ID_product"
        if url.find("profile") > -1:
            return "ID_profile"
        if url.find("login") > -1:
            return "ID_login_site"
        if url.find("tools.descartes.teastore.webui"):
            return "ID_index"
        print(url)
        return "ID_unknown"


    def convert_log_file(
            self, filename, file_path: Path, writing_directory: Path
    ) -> bool:

        with open(file_path) as file:
            lines = file.readlines()

        data={}
        for line in lines:
            match = re.search(self.pattern, line)
            if match:
                groups = match.groups()
                if groups[1] == "SUCCESS":
                    id = self.random_with_N_digits(10)
                    end_time = datetime.strptime(groups[0], '%Y-%m-%d %H:%M:%S,%f')
                    response_time = timedelta(milliseconds=float(groups[3]))

                    start_time = end_time - response_time
                    data["start_" + str(id)] = {
                        "id": id,
                        "time": start_time,
                        "action": "CMD-START",
                        "cmd": self.get_cmd(groups[2])
                    }

                    data["end_" + str(id)] = {
                        "id": id,
                        "time": end_time,
                        "action": "CMD-ENDE",
                        "cmd": self.get_cmd(groups[2])
                    }

        final_data = dict(sorted(data.items(), key=lambda item: item[1]['time']))
        target_path = writing_directory / filename
        with open(target_path, "w") as file:
            for key, value in final_data.items():
                formated_str = f"[{value['id']}]\t{datetime.strftime(value['time'], '%Y-%m-%d %H:%M:%S.%f')}\t{value['action']}\t{value['cmd']}\n"
                decoded_string = bytes(formated_str, "latin-1").decode("unicode_escape")
                file.write(decoded_string)

    def random_with_N_digits(self, n):
        range_start = 10**(n-1)
        range_end = (10**n)-1
        return randint(range_start, range_end)


