from builtins import Exception
from Agents import Agents

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

import sys
import shutil
import configparser
import threading
import multiprocessing
from multiprocessing.pool import ThreadPool
from multiprocessing.pool import Pool

import time
import os

import numpy as np
import random

__author__ = 'sabat'

def plot_histogram(x, y, x_range, y_range, plot_bins, xlabel, ylabel, filename, dir_name):
    plt.close()
    # heatmap, xedges, yedges = np.histogram2d(x, y, bins=[100, 100], range=[[0.0, 50.], [0., 1.]])
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=plot_bins, range=[x_range, y_range])
    extent = [xedges[0], xedges[-1], yedges[0], 100*yedges[-1]]
    # extent = [0., 4., 0., 1.0]
    heatmap = np.rot90(heatmap)
    heatmap = np.flipud(heatmap)
    # fig2 = plt.figure()
    plt.pcolormesh(xedges, yedges, heatmap)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    plt.savefig(os.path.join(dir_name, str(filename).zfill(5)+'.png'))

def random_gen(type):
    if type is 'triangle':
        return np.random.triangular(0, 0.5, 1)
    elif type is 'uniform':
        return np.random.random()
    else:
        raise Exception("Unsupported generator type for {}".format(type))

def function_to_thread(function, result):
    result = function()

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
        random_noise_gen = config.get("model", "random_noise_gen")
        p = config.getfloat("model", "p")
        alpha = config.getfloat("model", "alpha")
        aaa = list(map(float, config.get("model", "a").split(',')))

        steps1 = config.getint("simulation", "steps1")
        steps2 = config.getint("simulation", "steps2")
        output_path = config.get("simulation", "output_path")
        hist_gen_freq = config.getint("simulation", "hist_gen_freq")
        seed = config.getint("simulation", "seed", fallback=random.randint(0, sys.maxsize))
        curr_date = time.strftime('%Y%m%d-%H%M%S')
        path = os.path.join("outputs", output_path, curr_date)
        if not os.path.exists(path):
            os.makedirs(path)
    # creating buffer dir for remote syncing outputs
    rsync_path = os.path.join("rsync", output_path, curr_date)
    if not os.path.exists(rsync_path):
        os.makedirs(rsync_path)
    shutil.copy(conf_file_path, rsync_path)
    pool = ThreadPool(6)
    process_pool = Pool(4)
    for a in aaa:
        agents = Agents(n, k, a, p, clients_limit, alpha, random_noise_gen, seed)
        agents.setup()

        seed_file = open(os.path.join(rsync_path, "seeds.txt"), 'w')
        seed_file.write("[seeds]\n")
        seed_file.write("seed="+str(seed)+"\n")
        seed_file.close()

        test = time.time()
        curr_time = time.strftime('%H%M%S')
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
            results = []
            results.append(pool.apply_async(agents.get_average_w))
            results.append(pool.apply_async(agents.get_variance_w))
            results.append(pool.apply_async(agents.get_average_buyer_payoff))
            results.append(pool.apply_async(agents.get_average_seller_payoff))
            if i % hist_gen_freq is 0:
                sellers = list(agents.sellers)
                process_pool.apply_async(plot_histogram, args=(list(agents.sellers_count), sellers, [0.0, 50.], [0.0, 1.0], [50, 100], 'k', 'w', i, hist_dirpath))
                process_pool.apply_async(plot_histogram, args=(sellers, agents.get_seller_payoffs(), [0.0, 1.], [0.0, 20.0], [80, 80], 'w', 'P_seller',  i, seller_payoff_hist_dirpath))

            results = [result.get() for result in results]

            average_w = results[0]
            std_w = results[1]
            average_buyer_payoff = results[2]
            average_seller_payoff = results[3]

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
        pool.close()
        pool.join()
        print("Moving {} to {}".format(os.path.join(path, curr_time), rsync_path))
        shutil.move(os.path.join(path, curr_time), rsync_path)
