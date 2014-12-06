__author__ = 'sabat'

import random
import multiprocessing as mp
import math
import itertools


class Agents:
    def __init__(self, size, k, a, seed=12345):
        random.seed(seed)
        self.size = size
        self.k = k
        self.a = a
        self.buyers_grid = [None] * self.size
        self.sellers = [None] * self.size
        self.test = 0

    def setup(self):
        for i in range(self.size):
            row = [0] * self.k
            index = 0
            for agent in random.sample(range(self.size), self.k):
                row[index] = agent
                index += 1
            self.buyers_grid[i] = row

            self.sellers[i] = random.random()

    def buyer_payoff(self, index):
        result = 0.0
        for agent in range(self.buyers_grid[index]):
            result += self.sellers[agent]
        return result

    def count_buyers(self, index, start, end):
        result = 0
        if end > self.size:
            end = self.size
        for i in range(start, end):
            self.test += 1
            if index in self.buyers_grid[i]:
                result += 1
        return result

    def seller_payoff(self, index):
        result222 = 0
        processes = 1
        self.test = 0

        starts = range(0, self.size + self.size % processes, math.ceil(self.size / processes));
        ends = range(math.ceil(self.size / processes), self.size + self.size % processes,
                     math.ceil(self.size / processes));

        with mp.Pool(processes) as pool:
            params = zip(itertools.repeat(index), starts, ends)
            pool_values = [pool.apply_async(self.count_buyers, args).get() for args in params]
            for value in pool_values:
                result222 += value
        return result222 * self.sellers[index]

    def buyer_update(self, index):

        old = self.buyers_grid[index][random.randrange(0, self.k)]
        value_old = self.sellers[old]

        new = 0
        value_new = 0
        while True:
            new = random.randrange(0, self.size)
            if new not in self.buyers_grid[index]:
                value_new = self.sellers[new]
                break

        if value_new > value_old:
            self.buyers_grid[index].remove(old)
            self.buyers_grid[index].append(new)

    def seller_update(self, index):
        compare_to = index
        while compare_to is index:
            compare_to = random.randrange(0, self.size)
        if self.seller_payoff(compare_to) > self.seller_payoff(index):
            self.sellers[index] = self.sellers[compare_to]

    def random_noise(self):
        self.sellers[random.randrange(0, self.size)] = random.random()

    def iterate(self, steps):
        for i in range(steps):
            self.random_noise()
            if random.random() < self.a:
                self.seller_update(random.randrange(0, self.size))
            else:
                self.buyer_update(random.randrange(0, self.size))

    def get_average_w(self):
        return sum(self.sellers) / self.size


if __name__ == '__main__':
    agents = Agents(10, 3, 0.1)
    agents.setup()
    f = open('output2.txt', 'w')
    mp.freeze_support()
    for i in range(100):
        print("Calculating: ", i)
        f.write(str(agents.get_average_w()) + "\n")
        agents.iterate(i * 10000)

    f.close()
