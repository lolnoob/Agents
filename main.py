from builtins import Exception
from Agents import Agents

__author__ = 'sabat'

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
import shutil
import configparser

import time
import os

import numpy as np


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
    filename, ext = os.path.splitext(conf_file_path)
    if conf_exists and ext is 'ini':
        config = configparser.ConfigParser()
        config.read(conf_file_path)
        if ["model", "simulation"] not in config.sections():
            raise Exception("Wrong config file content")

        n = config.getint("model", "n")
        k = config.getint("model", "k")
        clients_limit = config.getint("model", "clients_limit")
        p = config.getfloat("model", "p")
        aaa = list(map(float, config.get("model", "a")))

        steps1 = config.getint("simulation", "steps1")
        steps2 = config.getint("simulation", "steps2")
        output_path = config.get("simulation", "output_path")
        path = os.path.join("outputs", output_path, time.strftime('%Y%m%d'))
    # creating buffer dir for remote syncing outputs
    rsync_path = "rsync"
    if not os.path.exists(rsync_path):
        os.makedirs(rsync_path)
    for a in aaa:
        print('n={}, k={}, a={}, steps1={}, steps2={}, p={}, max_clients={}'.format(n, k, a, steps1, steps2, p,
                                                                                    clients_limit))
        agents = Agents(n, k, a, p, clients_limit)
        agents.setup()
        test = time.time()
        if not os.path.exists(path):
            os.makedirs(path)
        to_format = '{}_output_n{}_k{}_a{}_steps1{}_steps2{}_p{}_maxclients{}'
        hist_dirname = to_format.format(time.strftime('%Y%m%d_%H%M%S'), n, k, a, steps1, steps2, p,
                                                                                    clients_limit)
        filename = hist_dirname + ".txt"
        hist_dirname = os.path.join(path, hist_dirname)
        if not os.path.exists(hist_dirname):
            os.makedirs(hist_dirname)
        filename = os.path.join(path, filename)
        f = open(filename, 'w')
        for i in range(steps1):
            average = agents.get_average_w()
            # if i % 100 is 0:
            # print(time.strftime('%Y%m%d_%H%M%S') + ": Calculating: ", i, " in time: ", str(test - time.time()), " with average: ", str(average))
            test = time.time()
            if i % 10 is 0:
                plot_histogram(agents.sellers_count, agents.sellers, hist_dirname)
            f.write(str(average) + "\n")
            f.flush()
            agents.iterate(steps2)

        f.close()

        print("Moving % to %".format(filename, rsync_path))
        shutil.move(filename, rsync_path)
        print("Moving % to %".format(hist_dirname, rsync_path))
        shutil.move(hist_dirname, rsync_path)

