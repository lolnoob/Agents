__author__ = 'sabat'

import random
import time
import os

import numpy.random as nprnd


class Agents:
    def __init__(self, size, k, a, p=0.0):
        self.size = size  # number of agents
        self.k = k  # fixed number of sellers for a single buyer
        self.a = a  # seller strategy update propability
        self.p = p  # random noise occurance propability
        self.buyers_grid = [None] * self.size  # list of list of sellers of every buyer
        self.sellers_count = [0 for i in range(self.size)]  # number of buyers connected to every seller
        self.sellers = [None] * self.size  #list of seller's prices w

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
        return self.sellers_count[index] * (1 - self.sellers[index])

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


if __name__ == '__main__':
    n = 1000000
    k = 3
    a = 0.35
    steps1 = 100000
    steps2 = 100000
    p = 0.0
    path = "outputs/" + time.strftime('%Y%m%d')
    # for a in [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9]: #for series of runs K=1
    # for a in [0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9]: #for series of runs K=3
    for p in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:  # for series of runs
        # for i in [1]:  #for a single run
        print('n={}, k={}, a={}, steps1={}, steps2={}, p={}'.format(n, k, a, steps1, steps2, p))
        agents = Agents(n, k, a, p)
        agents.setup()
        test = time.time()
        if not os.path.exists(path):
            os.makedirs(path)
        f = open(path + '/output_n{}_k{}_a{}_steps1{}_steps2{}_p{}.txt'.format(n, k, a, steps1, steps2, p), 'w')
        for i in range(steps1):
            average = agents.get_average_w()
            if i % 100 is 0:
                print("Calculating: ", i, " in time: ", str(test - time.time()), " with average: ", str(average))
                test = time.time()
            f.write(str(average) + "\n")
            agents.iterate(steps2)

        f.close()

