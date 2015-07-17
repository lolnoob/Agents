__author__ = 'sabat'

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import sys
import shutil

import random
import time
import os

import numpy.random as nprnd
import numpy as np


class Agents:
    def __init__(self, size, k, a, p=0.0, buyers_limit=-1):
        self.size = size  # number of agents
        self.k = k  # fixed number of sellers for a single buyer
        self.a = a  # seller strategy update propability
        self.p = p  # random noise occurance propability
        self.buyers_grid = [None] * self.size  # list of list of sellers of every buyer
        self.sellers_count = [0 for i in range(self.size)]  # number of buyers connected to every seller
        self.sellers = [None] * self.size  # list of seller's prices w
        self.buyers_limit = buyers_limit
        self.alpha = 0.1

    def setup(self):
        for i in range(self.size):
            row = [0] * self.k
            index = 0
            for agent in random.sample(range(self.size), self.k):
                row[index] = agent
                self.sellers_count[agent] += 1
                index += 1
            self.buyers_grid[i] = row

            self.sellers[i] = nprnd.random()

    def buyer_payoff(self, index):
        result = 0.0
        for agent in self.buyers_grid[index]:
            result += self.sellers[agent]
        return result

    def seller_payoff(self, index):
        clients = self.sellers_count[index]
        if 0 < self.buyers_limit < clients:
            clients = self.buyers_limit
        P = clients * (1 - self.sellers[index])
        return (P  / (1 + self.alpha*P*P))


    def buyer_update(self, index):
        old = self.buyers_grid[index][nprnd.randint(self.k)]
        value_old = self.sellers[old]

        new = nprnd.randint(self.size)
        while new in self.buyers_grid[index]:
            new = nprnd.randint(self.size)
        value_new = self.sellers[new]

        if value_new > value_old:
            self.buyers_grid[index].remove(old)
            self.sellers_count[old] -= 1
            self.buyers_grid[index].append(new)
            self.sellers_count[new] += 1

    def seller_update(self, index):
        compare_to = nprnd.randint(self.size)
        while compare_to is index:
            compare_to = nprnd.randint(self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[nprnd.randint(self.size)] = nprnd.random()
        # self.sellers[nprnd.randint(self.size)] = nprnd.triangular(0, 0.5, 1)

    def iterate(self, steps):
        for i in range(steps):
            if nprnd.random() < self.p:
                self.random_noise()
            index = nprnd.randint(0, self.size)
            if nprnd.random() < self.a:
                self.seller_update(index)
            else:
                self.buyer_update(index)

    def get_average_w(self):
        return sum(self.sellers) / self.size


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
    args = sys.argv
    n = 1000000
    k = int(args[1])
    aaa = list(map(float, args[2:]))
    steps1 = 10#0000
    steps2 = 10#0000
    clients_limit = -1
    p = 1e-6
    path = os.path.join("outputs", time.strftime('%Y%m%d'))
    # creating buffer dir for remote syncing outputs
    rsync_path = "rsync"
    if not os.path.exists(rsync_path):
            os.makedirs(rsync_path)
    # for a in [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9]: #for series of runs K=1
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
            print(time.strftime('%Y%m%d_%H%M%S') + ": Calculating: ", i, " in time: ", str(test - time.time()), " with average: ", str(average))
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

