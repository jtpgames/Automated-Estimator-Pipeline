import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def clean_cmd_name(cmd: str):
    start_pos = 0
    new_pos = 0
    # while new_pos > -1:
    #     start_pos = new_pos
    #     new_pos = cmd.find("/", start_pos + 1)

    end_pos = cmd.find("?")
    if end_pos == -1:
        end_pos = cmd.__len__()

    return cmd[start_pos + 1:end_pos]


pattern = re.compile("\[(SUCCESS|FAILURE)\]\[([a-zA-Z0-9-:,. \/=?&]*)\]\[([\d.]*)\]")


def get_response_times_by_cmd_type(df: pd.DataFrame):
    response_times = [df[df["type"] == "tools.descartes.teastore.webui/"]["response_time"]]
    labels = ["index"]
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/cartAction"]["response_time"])
    labels.append("cart_action")
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/category"]["response_time"])
    labels.append("category")
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/login"]["response_time"])
    labels.append("login")
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/loginAction"]["response_time"])
    labels.append("login_action")
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/product"]["response_time"])
    labels.append("product")
    response_times.append(df[df["type"] == "tools.descartes.teastore.webui/profile"]["response_time"])
    labels.append("profile")
    return response_times, labels

def compare_logs(real_log: str, sim_log: str):
    real_log_dict = get_processed_log(real_log)
    sim_log_dict = get_processed_log(sim_log)

    print("----------real----------")
    print(real_log_dict["df"])
    print("------------------------")

    print(real_log_dict["df"].groupby(["type"]).count())

    real_plotable_data, real_plot_labels = get_response_times_by_cmd_type(real_log_dict["df"])
    sim_plotable_data, sim_plot_labels = get_response_times_by_cmd_type(sim_log_dict["df"])
    plt.style.use('_mpl-gallery')

    # plot real
    fig_real, ax_real = plt.subplots(figsize=(5,5), layout="constrained")
    ax_real.set_title("real")
    VP_real = ax_real.boxplot(real_plotable_data, labels=real_plot_labels, showfliers=False)

    # plot real
    fig_sim, ax_sim = plt.subplots(figsize=(5,5), layout="constrained")
    ax_sim.set_title("sim")
    VP_sim = ax_sim.boxplot(sim_plotable_data, labels=sim_plot_labels, showfliers=False)
    plt.show()

def get_processed_log(locust_log):
    with open(locust_log) as logfile:
        lines = logfile.readlines()

    data = {"type": [], "response_time": []}
    failure_counter = 0
    for line in lines:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if groups[0] == "SUCCESS":
                data["type"].append(clean_cmd_name(groups[1]))
                data["response_time"].append(float(groups[2]))
            else:
                failure_counter += 1

    return {"df": pd.DataFrame(data), "failure_count": failure_counter}


def extract_kieker_command_mapping_from_middleware(filename: str):
    data = {"cmd": [], "url": []}
    with open(filename) as file:
        lines = file.readlines()

    for line in lines:
        cut_pos = line.find("///")
        data["cmd"].append(line[0:cut_pos])
        url = line[cut_pos + 3: get_position_of_last_str_char(line)]
        url = extract_command(url)
        data["url"].append(url)

    df = pd.DataFrame(data)
    # print(df[df['cmd'] == 'CartActionServlet_handleGETRequest'])
    print(df.groupby(["cmd"]).count())


def get_position_of_last_str_char(line):
    pos = line.find('\n')
    if pos > -1:
        return pos
    else:
        return line.__len__()


prefix = "/tools.descartes.teastore.webui/"


def remove_prefix(text: str, prefix: str) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def extract_command(url: str):
    # print(url)

    if url == "/":
        print("empty response")
        return
        # return Response(content="Empty response", media_type="text/plain")

    # command = request.url.path.removeprefix(prefix)
    if url != prefix:
        command = remove_prefix(url, prefix)
    else:
        command = "index"

    # tid = request.scope['X-UID']
    # print(f"Cmd: {command}")
    return command


def extract_command_types_from_kieker_logs(filename: str):
    with open(filename) as file:
        lines = file.readlines()

    data = {"cmd": [], "count": []}
    for line in lines:
        data["cmd"].append(line[line.find("ID"):line.find("\n") - 1])
        data["count"].append(1)

    df = pd.DataFrame(data)
    print(df.groupby(["cmd"]).count())


def teastore_simulation_log(filename: str):
    with open(filename) as file:
        lines = file.readlines()

    # removes first localhost call
    # lines = lines[1:lines.__len__()]

    cut_sign = "///"

    data = {
    }
    for line in lines:
        cut_pos = line.find(cut_sign)
        try:
            exists = data[line[:cut_pos]]
        except KeyError:
            exists = False

        if exists:
            data[line[:cut_pos]].append(line[cut_pos + cut_sign.__len__(): line.find("\n")])
        else:
            data[line[:cut_pos]] = [line[cut_pos + cut_sign.__len__(): line.find("\n")]]

    cleaned_data = {"cmd": [], "url": []}
    for key in data.keys():
        urls = data[key]
        urls.sort(reverse=True)
        longest_url = urls[0]
        matching_index = 0

        not_matching = False
        while not not_matching:

            for url in data[key]:
                if matching_index == len(url):
                    not_matching = True
                if -1 == url.find(longest_url[:matching_index]):
                    not_matching = True
                if not_matching:
                    break
                matching_index += 1
        cleaned_data["cmd"].append(key)
        cleaned_data["url"].append(longest_url[:matching_index - 1])

    # print(cleaned_data)
    df = pd.DataFrame.from_records(cleaned_data)
    print(df)


# teastore_simulation_log("teastore_simulation.log")
# extract_command_types_from_kieker_logs("teastore-cmd_2023-01-07.log")
# extract_kieker_command_mapping_from_middleware("kieker_intermediate_mapping.txt")
compare_logs("50-percent-cpu-logs/real_locust.log", "50-percent-cpu-logs/sim_locust.log")
