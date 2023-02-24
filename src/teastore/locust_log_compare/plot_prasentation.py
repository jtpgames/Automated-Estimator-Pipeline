import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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

pattern = re.compile("\[(SUCCESS|FAILURE)\]\[([a-zA-Z0-9-:,. \/=?&%]*)\]\[([\d.]*)\]")
def get_processed_log(locust_log):
    with open(locust_log) as logfile:
        lines = logfile.readlines()

    data = {"type": [], "response_time": []}
    failure_counter = 0
    failure_data = {"type": []}
    for line in lines:
        match = re.search(pattern, line)
        if match:
            groups = match.groups()
            if groups[0] == "SUCCESS":
                data["type"].append(get_cmd(groups[1]))
                data["response_time"].append(float(groups[2]))
            else:
                failure_counter += 1
                failure_data["type"].append(data["type"].append(get_cmd(groups[1])))

    df_failure = pd.DataFrame(failure_data).groupby(["type"]).count()
    # print("failures: {}".format(failure_counter))

    return {"df": pd.DataFrame(data), "failure_count": failure_counter}

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

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)


def get_data(log_file: str):
    log_dict = get_processed_log(log_file)
    plotable_data, plot_labels = get_response_times_by_relevant_cmd_type(log_dict["df"])
    return plotable_data

def set_comparsion_boxplots(data_sim, data_real, ax):
    l_pos = np.array(range(len(data_real))) * 3 - 0.7
    r_pos = np.array(range(len(data_sim))) * 3 + 0.7

    bpl = ax.boxplot(data_real, positions=l_pos, sym='', widths=0.6)
    bpr = ax.boxplot(data_sim, positions=r_pos, sym='', widths=0.6)

    set_box_color(bpl, '#D7191C')  # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

def short_plot(real_log: str, sim_log: str, heading: str, cpu_usage: str):
    real_25_low = get_data("real/nn-25/low/locust_log.log")
    real_25_high = get_data("real/nn-25/high/locust_log.log")
    real_75_low = get_data("real/nn-75/low/locust_log.log")
    real_75_high = get_data("real/nn-75/high/locust_log.log")

    sim_25_low = get_data("sim/nn-25/low/locust_log.log")
    sim_25_high = get_data("sim/nn-25/high/locust_log.log")
    sim_75_low = get_data("sim/nn-75/low/locust_log.log")
    sim_75_high = get_data("sim/nn-75/high/locust_log.log")

    fig, axes = plt.subplots(nrows=2, ncols=2,sharex=True, sharey="row")

    # Set the ticks and ticklabels for all axes
    set_comparsion_boxplots(real_25_low, sim_25_low, axes[0,0])
    set_comparsion_boxplots(real_75_low, sim_75_low, axes[0,1])
    set_comparsion_boxplots(real_25_high, sim_25_high, axes[1,0])
    set_comparsion_boxplots(real_75_high, sim_75_high, axes[1,1])

    plt.sca(axes[0, 0])
    plt.grid(True)
    plt.sca(axes[0, 1])
    plt.grid(True)
    plt.sca(axes[1, 0])
    plt.grid(True)
    plt.sca(axes[1, 1])
    plt.grid(True)

    axes[0,0].set_title('niedrig - 25% CPU')
    axes[0,1].set_title('niedrig - 75% CPU')
    axes[1,0].set_title('hoch - 25% CPU')
    axes[1,1].set_title('hoch - 75% CPU')

    # draw temporary red and blue lines and use them to create a legend
    axes[0,0].plot([], c='#D7191C', label='Teastore')
    axes[0,0].plot([], c='#2C7BB6', label='Simulation')
    axes[0,0].legend()

    plt.setp(axes, xticks=range(0, len(relevant_columns) * 3, 3), xticklabels=["index", "login", "order", "category"], xlim=(-2, len(relevant_columns)*3))
    fig.tight_layout()
    fig.set_figwidth(12)
    fig.set_figheight(6)

    fig.supylabel('Millisekunden')
    fig.supxlabel('Anfragetyp')

    #fig.suptitle("Vergleich Lasttests zwischen Teastore und Simulation")
    #fig.subplots_adjust(top=0.85)
    fig.subplots_adjust(bottom=0.13)
    fig.subplots_adjust(left=0.08)
    #fig.show()
    plt.savefig("test.png")


relevant_columns = ["ID_index", "ID_login_site", "ID_order", "ID_category"]
def get_response_times_by_relevant_cmd_type(df: pd.DataFrame):
    arr = np.array(relevant_columns)
    typed_arr = []
    for type in arr:
        typed_arr.append(np.array(df[df["type"] == type]["response_time"].values.tolist()))
    return np.array(typed_arr, dtype=object), arr



short_plot("real/nn-75/low/locust_log.log", "sim/nn-75/low/locust_log.log", "niedrig", "75")