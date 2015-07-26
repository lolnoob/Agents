from builtins import Exception
from Agents import Agents

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
import shutil
import configparser

import time
import os

import numpy as np

__author__ = 'sabat'

def plot_histogram(x, y, dir_name):
    plt.close()
    # heatmap, xedges, yedges = np.histogram2d(x, y, bins=[100, 100], range=[[0.0, 50.], [0., 1.]])
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=[50, 100], range=[[0.0, 50.], [0., 1.]])
    extent = [xedges[0], xedges[-1], yedges[0], 100*yedges[-1]]
    # extent = [0., 4., 0., 1.0]
    heatmap = np.rot90(heatmap)
    heatmap = np.flipud(heatmap)
    # fig2 = plt.figure()
    plt.pcolormesh(xedges, yedges, heatmap)
    plt.xlabel('k')
    plt.ylabel('w')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    plt.savefig(os.path.join(dir_name, str(i).zfill(5)+'.png'))

if __name__ == '__main__':
    # we will read all the properties from a yml file
    args = sys.argv
    conf_file_path = args[1]

    conf_exists = os.path.exists(conf_file_path)
    avg_w_data_filename, ext = os.path.splitext(conf_file_path)
    if conf_exists and ext == '.ini':
        config = configparser.ConfigParser()
        config.read(conf_file_path)
        if not set(["model", "simulation"]).issubset(config.sections()):
            raise Exception("Wrong config file content")

        n = config.getint("model", "size")
        k = config.getint("model", "k")
        clients_limit = config.getint("model", "clients_limit")
        p = config.getfloat("model", "p")
        aaa = list(map(float, config.get("model", "a").split(',')))

        steps1 = config.getint("simulation", "steps1")
        steps2 = config.getint("simulation", "steps2")
        output_path = config.get("simulation", "output_path")
        hist_gen_freq = config.getint("simulation", "hist_gen_freq")

        curr_date = time.strftime('%Y%m%d-%H%M%S')
        path = os.path.join("outputs", output_path, curr_date)
        if not os.path.exists(path):
            os.makedirs(path)
    # creating buffer dir for remote syncing outputs
    rsync_path = os.path.join("rsync", output_path, curr_date)
    if not os.path.exists(rsync_path):
        os.makedirs(rsync_path)
    shutil.copy(conf_file_path, rsync_path)
    for a in aaa:
        agents = Agents(n, k, a, p, clients_limit)
        agents.setup()
        test = time.time()
        curr_time = time.strftime('%H%M%S')
        os.makedirs(curr_time)
        hist_dirpath = os.path.join(path, curr_time, "histograms")
        seller_payoff_hist_dirpath = os.path.join(path, curr_time, "seller_payoff_histograms")
        if not os.path.exists(hist_dirpath):
            os.makedirs(hist_dirpath)
        if not os.path.exists(seller_payoff_hist_dirpath):
            os.makedirs(seller_payoff_hist_dirpath)
        avg_w_data_filename = os.path.join(path, curr_time, "avg_w.txt")
        std_w_data_filename = os.path.join(path, curr_time, "std_w.txt")
        avg_buyer_payoff_data_filename = os.path.join(path, curr_time, "avg_buyer_payoff.txt")
        avg_seller_payoff_data_filename = os.path.join(path, curr_time, "avg_seller_payoff.txt")
        f1 = open(avg_w_data_filename, 'w')
        f2 = open(std_w_data_filename, 'w')
        f3 = open(avg_buyer_payoff_data_filename, 'w')
        f4 = open(avg_seller_payoff_data_filename, 'w')
        for i in range(steps1):
            average_w = agents.get_average_w()
            std_w = agents.get_variance_w()
            average_buyer_payoff = agents.get_average_buyer_payoff()
            average_seller_payoff = agents.get_average_seller_payoff()
            if i % hist_gen_freq is 0:
                plot_histogram(agents.sellers_count, agents.sellers, hist_dirpath)
                plot_histogram(agents.sellers_count, agents.get_seller_payoffs(), seller_payoff_hist_dirpath)
            f1.write(str(average_w) + "\n")
            f2.write(str(std_w) + "\n")
            f3.write(str(average_buyer_payoff) + "\n")
            f4.write(str(average_seller_payoff) + "\n")
            f1.flush()
            f2.flush()
            f3.flush()
            f4.flush()
            agents.iterate(steps2)

        f1.close()
        f2.close()
        f3.close()
        f4.close()

        print("Moving {} to {}".format(os.path.join(path, curr_time), rsync_path))
        shutil.move(os.path.join(path, curr_time), rsync_path)
