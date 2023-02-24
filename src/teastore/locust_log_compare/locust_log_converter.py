import re

import uuid as uuid
from datetime import datetime, timedelta
from random import randint

pattern = re.compile("\[([0-9- :,]*)\].*\[(SUCCESS|FAILURE)\]\[([a-zA-Z0-9-:,. \/=?&%]*)\]\[([\d.]*)\]")
def convert_logs(filename: str):
    with open(filename) as file:
        lines = file.readlines()

    data={}
    for line in lines:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if groups[1] == "SUCCESS":
                id = random_with_N_digits(10)
                end_time = datetime.strptime(groups[0], '%Y-%m-%d %H:%M:%S,%f')
                response_time = timedelta(milliseconds=float(groups[3]))

                start_time = end_time - response_time
                data["start_" + str(id)] = {
                    "id": id,
                    "time": start_time,
                    "action": "CMD-START",
                    "cmd": get_cmd(groups[2])
                }

                data["end_" + str(id)] = {
                    "id": id,
                    "time": end_time,
                    "action": "CMD-ENDE",
                    "cmd": get_cmd(groups[2])
                }

    final_data = dict(sorted(data.items(), key=lambda item: item[1]['time']))
    print_to_file(final_data)
    #print(data)

def print_to_file(data: dict):
    with open("export.log", "w") as file:
        for key, value in data.items():
            formated_str = f"[{value['id']}]\t{datetime.strftime(value['time'], '%Y-%m-%d %H:%M:%S.%f')}\t{value['action']}\t{value['cmd']}\n"
            decoded_string = bytes(formated_str, "latin-1").decode("unicode_escape")
            file.write(decoded_string)




def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)


def get_cmd(url: str) -> str:
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


convert_logs("real_75_low.log")