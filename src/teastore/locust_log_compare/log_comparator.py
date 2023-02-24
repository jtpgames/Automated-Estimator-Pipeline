import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import ttest_ind, ks_2samp, mannwhitneyu, stats, kstest, zscore

def plot(real_log: str, sim_log: str, heading: str, cpu_usage: str):
    real_log_dict = get_processed_log(real_log)
    sim_log_dict = get_processed_log(sim_log)

    print(f"{heading} - {cpu_usage}")
    mannwhitneyu_custom(real_log_dict["df"], sim_log_dict["df"])

    real_plotable_data, real_plot_labels = get_response_times_by_cmd_type(real_log_dict["df"])
    m_real = [x.mean() for x in real_plotable_data]
    std_real = [x.std() for x in real_plotable_data]

    sim_plotable_data, sim_plot_labels = get_response_times_by_cmd_type(sim_log_dict["df"])
    m_sim = [x.mean() for x in sim_plotable_data]
    std_sim = [x.std() for x in sim_plotable_data]

    fig, ax = plt.subplots()
    fig.set_figwidth(17)
    l_pos = np.array(range(len(real_plotable_data))) * 3 - 0.7
    r_pos = np.array(range(len(sim_plotable_data))) * 3 + 0.7

    bpl = ax.boxplot(real_plotable_data, positions=l_pos, sym='', widths=0.6, showmeans=True)
    bpr = ax.boxplot(sim_plotable_data, positions=r_pos, sym='', widths=0.6, showmeans=True)

    # include mean and std in plot
    for i, line in enumerate(bpl['medians']):
        x, y = line.get_xydata()[1]
        text = ' μ={:.2f}\n σ={:.2f}'.format(m_real[i], std_real[i])
        ax.annotate(text, xy=(x, y))

    # include mean and std in plot
    for i, line in enumerate(bpr['medians']):
        x, y = line.get_xydata()[1]
        text = ' μ={:.2f}\n σ={:.2f}'.format(m_sim[i], std_sim[i])
        ax.annotate(text, xy=(x, y))

    set_box_color(bpl, '#D7191C')  # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    # draw temporary red and blue lines and use them to create a legend
    plt.plot([], c='#D7191C', label='Teastore')
    plt.plot([], c='#2C7BB6', label='Simulation')
    plt.legend()

    plt.xticks(range(0, len(real_plot_labels) * 3, 3), real_plot_labels)
    plt.xlim(-2, len(real_plot_labels) * 3)

    plt.grid(visible=True, alpha=0.3)
    plt.ylabel('Millisekunden', labelpad=10)
    plt.xlabel('Anfragetyp', labelpad=10)
    plt.tight_layout()
    plt.title(
        "Locust Nutzerkonfiguration: " + heading + " - " + "zusätzlich erzeugte CPU Auslastung: " + cpu_usage + "%")
    plt.subplots_adjust(top=0.9)

    # plt.boxplot(merged_plotable_data, patch_artist=True, labels=merged_plot_labels, showfliers=False, notch=True, widths=0.7, showmeans=True)
    # plt.show()
    plt.savefig('{}_{}_comparsion.png'.format(cpu_usage, heading))

def short_plot(real_log: str, sim_log: str, heading: str, cpu_usage: str):
    real_log_dict = get_processed_log(real_log)
    sim_log_dict = get_processed_log(sim_log)

    print(f"{heading} - {cpu_usage}")
    mannwhitneyu_custom(real_log_dict["df"], sim_log_dict["df"])

    real_plotable_data, real_plot_labels = get_response_times_by_relevant_cmd_type(real_log_dict["df"])
    m_real = [x.mean() for x in real_plotable_data]
    std_real = [x.std() for x in real_plotable_data]

    sim_plotable_data, sim_plot_labels = get_response_times_by_relevant_cmd_type(sim_log_dict["df"])
    m_sim = [x.mean() for x in sim_plotable_data]
    std_sim = [x.std() for x in sim_plotable_data]

    fig, ax = plt.subplots(nrows=1, ncols=2)
    #fig.set_figwidth(8)
    l_pos = np.array(range(len(real_plotable_data))) * 3 - 0.7
    r_pos = np.array(range(len(sim_plotable_data))) * 3 + 0.7

    bpl = ax[1].boxplot(real_plotable_data, positions=l_pos, sym='', widths=0.6, showmeans=True)
    bpr = ax[1].boxplot(sim_plotable_data, positions=r_pos, sym='', widths=0.6, showmeans=True)

    set_box_color(bpl, '#D7191C')  # colors are from http://colorbrewer2.org/
    set_box_color(bpr, '#2C7BB6')

    # draw temporary red and blue lines and use them to create a legend
    ax[1].plot([], c='#D7191C', label='Teastore')
    ax[1].plot([], c='#2C7BB6', label='Simulation')
    ax[1].legend()

    ax[1].xticks(range(0, len(real_plot_labels) * 3, 3), real_plot_labels)
    ax[1].xlim(-2, len(real_plot_labels) * 3)

    ax[1].grid(visible=True, alpha=0.3)
    ax[1].ylabel('Millisekunden', labelpad=10)
    ax[1].xlabel('Anfragetyp', labelpad=10)
    plt.tight_layout()
    plt.title(
        "Locust Nutzerkonfiguration: " + heading + " - " + "zusätzlich erzeugte CPU Auslastung: " + cpu_usage + "%")
    plt.subplots_adjust(top=0.9)

    # plt.boxplot(merged_plotable_data, patch_artist=True, labels=merged_plot_labels, showfliers=False, notch=True, widths=0.7, showmeans=True)
    plt.show()
    #plt.savefig('{}_{}_comparsion.png'.format(cpu_usage, heading))

def set_box_color(bp, color):
    plt.setp(bp['boxes'], color=color)
    plt.setp(bp['whiskers'], color=color)
    plt.setp(bp['caps'], color=color)
    plt.setp(bp['medians'], color=color)


def merge_data(real_data, sim_data, real_names, sim_names):
    data = []
    names = []
    for x in range(0, real_data.__len__()):
        data.append(real_data[x])
        data.append(sim_data[x])
        names.append(real_names[x])
        names.append("")
    return data, names


def test_ttest(df1, df2):
    group1 = df1[df1["type"] == "ID_login"]
    group2 = df2[df2["type"] == "ID_login"]
    print(ttest_ind(group1["response_time"], group2["response_time"], equal_var=False))
    print(ks_2samp(group1["response_time"], group2["response_time"]))



indices = []


def mannwhitneyu_custom(df1, df2):
    global indices
    if indices.__len__() == 0:
        indices = df1["type"].unique()
    for type in indices:
        group1 = df1[df1["type"] == type]
        group2 = df2[df2["type"] == type]
        U, p = mannwhitneyu(zscore(group1["response_time"]), zscore(group2["response_time"]))
        print(
            "{}: {:.3f} - {}".format(type, p, kstest(zscore(group1["response_time"]), zscore(group2["response_time"]))))


def get_max_val(arr):
    max_value = 0
    for x in arr:
        for y in x:
            if y > max_value:
                max_value = y
    return max_value


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

relevant_columns = ["ID_index", "ID_login_site", "ID_order", "ID_category"]
def get_response_times_by_cmd_type(df: pd.DataFrame):
    types_df = df["type"].unique()
    arr = np.array(types_df)
    typed_arr = []
    for type in arr:
        typed_arr.append(np.array(df[df["type"] == type]["response_time"].values.tolist()))
    return np.array(typed_arr, dtype=object), arr


def get_response_times_by_relevant_cmd_type(df: pd.DataFrame):
    arr = np.array(relevant_columns)
    typed_arr = []
    for type in arr:
        typed_arr.append(np.array(df[df["type"] == type]["response_time"].values.tolist()))
    return np.array(typed_arr, dtype=object), arr


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


# plot("real/nn-25/low/locust_log.log", "sim/nn-25/low/locust_log.log", "niedrig", "25")
# plot("real/nn-25/mid/locust_log.log", "sim/nn-25/mid/locust_log.log", "mittel", "25")
# plot("real/nn-25/high/locust_log.log", "sim/nn-25/high/locust_log.log", "hoch", "25")
#
# plot("real/nn-50/low/locust_log.log", "sim/nn-50/low/locust_log.log", "niedrig", "50")
# plot("real/nn-50/mid/locust_log.log", "sim/nn-50/mid/locust_log.log", "mittel", "50")
# plot("real/nn-50/high/locust_log.log", "sim/nn-50/high/locust_log.log", "hoch", "50")
#
short_plot("real/nn-75/low/locust_log.log", "sim/nn-75/low/locust_log.log", "niedrig", "75")
# plot("real/nn-75/mid/locust_log.log", "sim/nn-75/mid/locust_log.log", "mittel", "75")
# plot("real/nn-75/high/locust_log.log", "sim/nn-75/high/locust_log.log", "hoch", "75")
