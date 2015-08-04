import random
import math
import numpy as np
from numpy import random as nprnd

__author__ = 'tsabala'


class Agents:
    def __init__(self, size, k, a, p=0.0, buyers_limit=-1, alpha=0, random_noise_type="uniform", seed = None):
        self.size = size  # number of agents
        self.k = k  # fixed number of sellers for a single buyer
        self.a = a  # seller strategy update probability
        self.p = p  # random noise occurrence probability
        self.buyers_grid = [None] * self.size  # list of list of sellers of every buyer
        self.sellers_count = [0 for i in range(self.size)]  # number of buyers connected to every seller
        self.sellers = [None] * self.size  # list of seller's prices w
        self.buyers_limit = buyers_limit
        self.alpha = alpha  # tax curve causing with local minimum 1/(1+alpha*x^x)
        self.random_noise_type = random_noise_type  # random gen used for generating noise to the system
        random.seed(seed)
        nprnd.seed(seed)

    def setup(self):
        for i in range(self.size):
            row = [0] * self.k
            index = 0
            for agent in random.sample(range(self.size), self.k):
                row[index] = agent
                self.sellers_count[agent] += 1
                index += 1
            self.buyers_grid[i] = row

            self.sellers[i] = self.get_random()

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
        return P / (1+self.alpha*P*P)

    def get_seller_payoffs(self):
        return list(map(self.seller_payoff, range(self.size)))

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
        self.sellers[nprnd.randint(self.size)] = self.get_random()

    def get_random(self):
        if self.random_noise_type == 'triangle':
            rand = np.random.triangular(0, 0.5, 1)
        elif self.random_noise_type == 'uniform':
            rand =  np.random.random()
        else:
            raise Exception("Unsupported generator type for {}".format(self.random_noise_type))
        return rand

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
        return np.mean(self.sellers)

    def get_variance_w(self):
        return np.std(self.sellers)

    def get_average_seller_payoff(self):
        return np.mean(self.get_seller_payoffs())

    def get_average_buyer_payoff(self):
        return np.mean(list(map(self.buyer_payoff, range(self.size))))
